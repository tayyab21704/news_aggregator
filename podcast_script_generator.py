# services/podcast_script_generator.py
import json
import datetime # For current time in prompt
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os # To load API keys if running standalone

class PodcastScriptGenerator:
    def __init__(self, llm_model_name: str = "gemini-1.5-pro-latest"):
        self.llm = ChatGoogleGenerativeAI(model=llm_model_name, temperature=0.7) # Higher temperature for creativity

        # --- REFINED SYSTEM PROMPT TEMPLATE ---
        self.system_prompt_template = """
        You are an expert podcast scriptwriter for a news show with two hosts:
        - **Host A (Narrator/Facilitator):** Calm, engaging, introduces news topics, sets the scene, and asks clarifying questions.
        - **Host B (Analyst/Fact-Checker/Debater):** Sharp, analytical, interjects with insights on bias, aggressive tone, factual corrections (citing sources), and presents contrasting factual perspectives from other news sources. Host B is data-driven but conversational.

        Your task is to create a dynamic, conversational script based on the detailed JSON analysis of one or more news articles provided below. The hosts should sound like two friends discussing current events, but with deep factual and analytical insights.

        **Strict Guidelines for Script Generation:**
        1.  **Format:** Each line of dialogue MUST be clearly prefixed with "Host A:" or "Host B:".
        2.  **Introduction:** Start with a friendly, casual intro by Host A, followed by Host B's acknowledgement.
        3.  **Topic Introduction:** Host A introduces the main news topic using key objective points from the first article's analysis.
        4.  **Integrating Bias & Tone:**
            * Host B MUST interject when bias or aggressive tone is detected.
            * For **bias regions**: Clearly state the source, quote the biased phrase, briefly explain its bias type/impact based on the analysis. (e.g., "Looking at [Source X], they used the phrase '[biased_snippet]'. Our analysis flags this as [bias_type] bias, indicating it leans [overall_bias_direction].")
            * For **aggressive tone**: Point out specific aggressive wording and its effect. (e.g., "And the tone in [Source Y]'s report, using words like '[aggressive_word]', feels quite aggressive for a news piece, designed to evoke [emotion].")
        5.  **Integrating Fact-Checks & Corrections:**
            * If `fact_checked_claims` show a claim is 'False' or 'Partially True/Misleading':
                * Host B MUST correct the misinformation. State clearly that the claim is incorrect, provide the `corrected_fact`, and **cite the `supporting_url`** from the fact-check. (e.g., "I have to jump in here, Host A. While [Source Z] claimed '[original_claim_text]', our fact-check actually found it to be [status]. The corrected fact, according to [supporting_url], is '[corrected_fact]'.")
        6.  **Contrasting Perspectives/Debate (if multiple articles):**
            * If `analysis_reports` contain multiple articles on the same topic, Host A should prompt Host B to introduce the other perspectives.
            * Host B should then present key *factual* differences or different *emphasis* between the articles. This is a debate purely on facts and framing, not opinion. (e.g., "On the same topic, [Source B] focused more on [different factual aspect]. While both are factual, it gives a slightly different picture than [Source A]'s emphasis on [Source A's emphasis].")
        7.  **Conversational Flow:** Maintain the tone of two knowledgeable friends discussing, not reading a script. Use transitions.
        8.  **Listener Empowerment & Call to Action:** Conclude by empowering the listener to make their own judgments and encourage them to use the app's voting/feedback system.
        9.  **Length:** Keep the overall podcast concise (aim for 2-5 minutes of speaking time, which translates to a few hundred words).

        **Detailed Analysis Reports (JSON Array):**
        {analysis_reports_json}
        """

    def generate_script(self, analysis_reports: List[Dict[str, Any]]) -> str:
        """Generates the podcast script based on detailed article analysis reports."""
        if not analysis_reports:
            return "Host A: Sorry, we couldn't find any news to discuss today. Please check back later!"

        # Pass the analysis reports as a JSON string within the human message
        # The system prompt clearly defines the JSON structure to expect.
        analysis_reports_json = json.dumps(analysis_reports, indent=2)

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt_template),
            ("human", "Generate the podcast script based on the analysis. Ensure it's conversational and follows all guidelines. The current time is {current_time_ist} in Pune, Maharashtra, India. Start the podcast as if it's airing now.".format(current_time_ist=datetime.datetime.now().strftime("%I:%M:%S %p IST on %A, %B %d, %Y"))) # Inject current time/location
        ])

        chain = prompt | self.llm
        try:
            response = chain.invoke({"analysis_reports_json": analysis_reports_json})
            script_content = response.content
            # Basic validation: ensure it contains both hosts
            if "Host A:" not in script_content or "Host B:" not in script_content:
                print("WARNING: Generated script does not contain both hosts. Retrying or falling back.")
                # You could add retry logic here, or a simpler fallback script
                return self._fallback_script(analysis_reports, script_content)
            return script_content
        except Exception as e:
            print(f"ERROR: Failed to generate podcast script: {e}")
            return self._fallback_script(analysis_reports, f"LLM Error: {e}")

    def _fallback_script(self, analysis_reports: List[Dict[str, Any]], error_message: str = "Script generation failed.") -> str:
        """Provides a simple fallback script if LLM generation fails."""
        first_article_title = "a recent news topic"
        if analysis_reports and analysis_reports[0]['article_data']['title']:
            first_article_title = analysis_reports[0]['article_data']['title']
        
        fallback_text = f"""
Host A: Welcome to our news update. We encountered a technical hiccup in generating our usual in-depth analysis today.
Host B: Yes, seems our AI hosts are having a brief coffee break. But we can tell you that {first_article_title} was a significant event today.
Host A: We apologize for the issue and will bring you a full, unbiased, and fact-checked report as soon as possible.
Host B: In the meantime, remember to always critically assess your news sources.
Host A: More updates soon!
"""
        if error_message != "Script generation failed.":
            fallback_text += f"\n\n(Internal Error: {error_message})" # Add internal error for debugging
        return fallback_text


# Example Usage (for testing this module directly)
if __name__ == "__main__":
    # --- IMPORTANT: Ensure .env is loaded for GOOGLE_API_KEY ---
    from dotenv import load_dotenv
    load_dotenv()

    # --- NEW: Import AnalysisEngine and DataLoader ---
    from services.analysis_engine import AnalysisEngine
    from services.data_loader import load_articles_from_files

    # --- Define your absolute file paths for testing ---
    file1path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article1_national_voice.txt"
    file2path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article2_vigilant_daily.txt"
    # If you have an article3_neutral_source.txt, define its path here as well.
    # file3path = r"C:\Users\hp\OneDrive\Desktop\News_aggre\test_data\article3_neutral_source.txt"

    # --- Initialize Analysis Engine ---
    analysis_engine = AnalysisEngine() # This will pick up GOOGLE_API_KEY and TAVILY_API_KEY

    # --- Prepare Analysis Reports for testing ---
    test_analysis_reports = []

    print("\n--- Preparing Analysis for Single Article Script ---")
    try:
        articles_single = load_articles_from_files([file1path])
        if articles_single:
            report_single = analysis_engine.analyze_article(articles_single[0])
            test_analysis_reports.append(report_single)
            print(f"Successfully prepared analysis for '{articles_single[0]['title']}'")
        else:
            print(f"Failed to load article from {file1path}.")
    except Exception as e:
        print(f"Error during single article analysis preparation: {e}")

    print("\n--- Preparing Analysis for Debate Script ---")
    try:
        articles_debate = load_articles_from_files([file1path, file2path])
        if len(articles_debate) == 2:
            # Analyze each article individually to get two reports
            report_debate_1 = analysis_engine.analyze_article(articles_debate[0])
            report_debate_2 = analysis_engine.analyze_article(articles_debate[1])
            test_analysis_reports_for_debate = [report_debate_1, report_debate_2]
            print(f"Successfully prepared analysis for debate between '{articles_debate[0]['title']}' and '{articles_debate[1]['title']}'")
        else:
            print(f"Failed to load both articles for debate (loaded {len(articles_debate)}).")
            test_analysis_reports_for_debate = [] # Ensure it's empty if not enough articles
    except Exception as e:
        print(f"Error during debate analysis preparation: {e}")


    # --- Generate Script using the prepared reports ---
    script_generator = PodcastScriptGenerator()

    # Test with the single report (from test_analysis_reports list, first element)
    if test_analysis_reports:
        print("\n--- Generating Podcast Script (Single Article) ---")
        script_single = script_generator.generate_script([test_analysis_reports[0]]) # Pass as a list with one item
        print(script_single)
    else:
        print("\n--- Skipping Single Article Script Generation: No analysis report available. ---")


    # Test with multiple reports for debate
    if test_analysis_reports_for_debate:
        print("\n--- Generating Podcast Script (Multiple Articles for Debate) ---")
        script_debate = script_generator.generate_script(test_analysis_reports_for_debate) # Pass the list of two reports
        print(script_debate)
    else:
        print("\n--- Skipping Debate Script Generation: Not enough analysis reports available. ---")