# services/analysis_engine.py
import os
import json
import time 
from typing import List, Dict, Any, Tuple

# Import backoff for robust retry logic
import backoff 

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from services.data_loader import load_articles_from_files

# Define a custom exception for LLM rate limits if LangChain's internal one isn't specific enough
from google.api_core.exceptions import ResourceExhausted

# Define a backoff handler for logging purposes
def backoff_hdlr(details):
    print(f"Backing off {details['wait']:0.1f} seconds after {details['tries']} tries "
          f"calling {details['target'].__name__} (caught {details['exception'].__class__.__name__}).")

# --- DEFINE JSON OUTPUT SCHEMAS AT THE TOP LEVEL (GLOBAL) ---
CLAIM_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "A unique identifier for the claim."},
                    "sentence": {"type": "string", "description": "The exact sentence from the article containing the claim."},
                    "text": {"type": "string", "description": "The isolated, concise factual statement within the sentence."},
                },
                "required": ["id", "sentence", "text"]
            }
        }
    }
}

BIAS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_bias_direction": {"type": "string", "description": "Overall political/emotional bias (e.g., 'Pro-XYZ Party', 'Anti-Opposition', 'Neutral', 'Highly Emotional')."},
        "overall_bias_percentage": {"type": "integer", "description": "Overall bias strength as a percentage (0 for neutral, 100 for extremely biased)."},
        "aggressive_tone_present": {"type": "boolean", "description": "True if aggressive or inflammatory tone is detected."},
        "bias_regions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "snippet": {"type": "string", "description": "The exact sentence or short paragraph showing bias."},
                    "bias_type": {"type": "string", "description": "Type of bias (e.g., 'Framing', 'Word Choice', 'Omission', 'Selection')."},
                    "bias_strength": {"type": "string", "description": "Strength of bias ('Low', 'Medium', 'High')."},
                    "explanation": {"type": "string", "description": "Brief explanation of why this snippet is biased."},
                },
                "required": ["snippet", "bias_type", "bias_strength", "explanation"]
            }
        }
    },
    "required": ["overall_bias_direction", "overall_bias_percentage", "aggressive_tone_present", "bias_regions"]
}

VERIFICATION_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["Correct", "False", "Partially True/Misleading", "Unverifiable"], "description": "Verification status of the claim."},
        "corrected_fact": {"type": "string", "description": "The correct factual statement, if the original claim was false or misleading. Empty if correct/unverifiable."},
        "explanation": {"type": "string", "description": "Brief explanation of the verification result, citing search results."},
        "supporting_url": {"type": "string", "description": "A URL from the search results that supports the verification. Empty if no clear URL."}
    },
    "required": ["status", "explanation"]
}


# --- 1. Initialize Tavily Search Tool ---
tavily_search_tool_instance = TavilySearch(max_results=2)
@tool
def search_web(query: str) -> str:
    """
    Searches the web for the given query using Tavily and returns relevant snippets.
    This tool is used by the LLM for fact-checking.
    """
    print(f"\n--- PERFORMING REAL WEB SEARCH (via Tavily): {query} ---")
    try:
        results = tavily_search_tool_instance.invoke({"query": query})
        if not results:
            return "No relevant search results found."
        return results
    except Exception as e:
        print(f"ERROR: Tavily search failed for query '{query}': {e}")
        return "Search failed or returned an error."


class AnalysisEngine:
    def __init__(self, llm_model_name: str = "gemini-1.5-pro-latest"):
        self.llm = ChatGoogleGenerativeAI(model=llm_model_name, temperature=0.2)
        self.search_tool = search_web

        escaped_claim_schema_str = json.dumps(CLAIM_OUTPUT_SCHEMA, indent=2).replace('{', '{{').replace('}', '}}')
        escaped_bias_schema_str = json.dumps(BIAS_OUTPUT_SCHEMA, indent=2).replace('{', '{{').replace('}', '}}')
        escaped_verification_schema_str = json.dumps(VERIFICATION_OUTPUT_SCHEMA, indent=2).replace('{', '{{').replace('}', '}}')

        self.claim_extractor_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert news analyst. Your task is to extract all explicit factual claims from the given text. Each claim must be a standalone verifiable statement, without opinion. Provide the exact sentence it comes from and a very concise, unique claim_text. Return the output as a JSON object strictly conforming to the following schema:\n\n" + escaped_claim_schema_str),
            ("human", "Text: {text}\nClaims:")
        ])
        
        self.bias_detector_prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze the following news article content for political and emotional bias. Identify specific 'bias regions' (sentences/paragraphs), describe the type and degree of bias, and note if the tone is aggressive. Provide an overall bias direction and percentage (0-100). Return the output as a JSON object strictly conforming to the following schema:\n\n" + escaped_bias_schema_str),
            ("human", "Article: {article_content}\nBias Analysis:")
        ])
        
        self.fact_checker_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a diligent fact-checker. Given a factual claim and relevant web search results, determine if the claim is factually accurate, partially true/misleading, or false/debunked. Provide a brief explanation and cite supporting URLs from the search results. If the claim is false or misleading, state the corrected fact. Return the output as a JSON object strictly conforming to the following schema:\n\n" + escaped_verification_schema_str),
            ("human", "Claim: {claim}\nSearch Results: {search_results}\nVerification:")
        ])

        # --- Apply backoff decorator to the LLM invocation methods ---
        # NOTE THE ADDITION OF 'self' AS THE FIRST ARGUMENT HERE
        @backoff.on_exception(
            backoff.expo, 
            ResourceExhausted, 
            max_tries=5, 
            max_time=60, 
            on_backoff=backoff_hdlr,
            factor=2, 
            jitter=backoff.full_jitter
        )
        def _invoke_llm_with_prompt(decorated_self, llm_instance, prompt_template, **kwargs):
            """Generic helper to invoke LLM with backoff.
               'decorated_self' is the instance of AnalysisEngine, needed because this nested function
               is being bound as a method."""
            return llm_instance.invoke(prompt_template.format_messages(**kwargs))

        # Bind this decorated function to the instance
        # We need to bind it explicitly because it's defined in __init__
        self._invoke_llm_with_prompt_bound = _invoke_llm_with_prompt.__get__(self, self.__class__)


    # --- Robust JSON Parsing Helper ---
    def _parse_llm_json_output(self, llm_response_content: str, schema_name: str = "Unknown") -> Dict[str, Any]:
        """Attempts to parse LLM string output as JSON, with error handling."""
        try:
            parsed_data = json.loads(llm_response_content)
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse {schema_name} JSON from LLM: {e}")
            print(f"LLM Raw Output:\n{llm_response_content[:500]}...")
            if schema_name == "claims":
                return {"claims": []}
            elif schema_name == "bias":
                return {"overall_bias_direction": "Parsing Error", "overall_bias_percentage": 0, "aggressive_tone_present": False, "bias_regions": []}
            elif schema_name == "verification":
                return {"status": "Parsing Error", "explanation": "LLM output invalid JSON."}
            return {}

    def _extract_claims(self, text: str) -> List[Dict[str, str]]:
        response = self._invoke_llm_with_prompt_bound(self.llm, self.claim_extractor_prompt, text=text)
        parsed_output = self._parse_llm_json_output(response.content, "claims")
        return parsed_output.get("claims", [])

    def _analyze_bias(self, article_content: str) -> Dict[str, Any]:
        response = self._invoke_llm_with_prompt_bound(self.llm, self.bias_detector_prompt, article_content=article_content)
        parsed_output = self._parse_llm_json_output(response.content, "bias")
        return parsed_output

    def _verify_claim(self, claim_data: Dict[str, str]) -> Dict[str, Any]:
        search_results_str = self.search_tool.invoke({"query": f"Is '{claim_data['text']}' true? fact check"})
        
        verification_response = self._invoke_llm_with_prompt_bound(
            self.llm, 
            self.fact_checker_prompt, 
            claim=claim_data['text'], 
            search_results=search_results_str
        )
        parsed_output = self._parse_llm_json_output(verification_response.content, "verification")
        return parsed_output

    def analyze_article(self, article_data: Dict[str, str]) -> Dict[str, Any]:
        """Performs full bias, tone, and fact-checking analysis on an article."""
        full_content = article_data['content']

        print(f"\n--- Analyzing Bias for: {article_data['title']} ---")
        bias_analysis = self._analyze_bias(full_content)

        print(f"--- Extracting Claims for: {article_data['title']} ---")
        claims = self._extract_claims(full_content)

        fact_checked_claims = []
        for claim_data in claims:
            print(f"--- Verifying Claim: '{claim_data['text']}' ---")
            verification_result = self._verify_claim(claim_data)
            fact_checked_claims.append({**claim_data, **verification_result})

        return {
            "article_data": article_data,
            "bias_analysis": bias_analysis,
            "fact_checked_claims": fact_checked_claims
        }

# Example Usage (for testing this module directly)
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    file1path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article1_national_voice.txt"
    file2path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article2_vigilant_daily.txt"

    engine = AnalysisEngine()

    print("\n--- TEST CASE: Analyzing Single Article from File ---")
    try:
        articles_from_file1 = load_articles_from_files([file1path])
        if articles_from_file1:
            analysis_report_single = engine.analyze_article(articles_from_file1[0])
            print("\n--- Full Analysis Report (Single Article) ---")
            print(json.dumps(analysis_report_single, indent=2))
        else:
            print(f"ERROR: Could not load article from {file1path} for analysis.")
    except Exception as e:
        print(f"An error occurred during single article analysis: {e}")

    print("\n--- TEST CASE: Analyzing Two Contrasting Articles for Debate ---")
    try:
        articles_for_debate = load_articles_from_files([file1path, file2path])
        
        if len(articles_for_debate) == 2:
            print("\n--- Analyzing First Article for Debate ---")
            analysis_report_debate_1 = engine.analyze_article(articles_for_debate[0])
            print(json.dumps(analysis_report_debate_1, indent=2))

            print("\n--- Analyzing Second Article for Debate ---")
            analysis_report_debate_2 = engine.analyze_article(articles_for_debate[1])
            print(json.dumps(analysis_report_debate_2, indent=2))

            print("\n--- Both articles loaded and analyzed for debate scenario. ---")

        else:
            print(f"ERROR: Expected 2 articles for debate, but loaded {len(articles_for_debate)}. Check file paths.")
    except Exception as e:
        print(f"An error occurred during debate article analysis: {e}")