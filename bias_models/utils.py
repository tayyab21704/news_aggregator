# utils.py

def read_input_text(filename="input.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("❌ input.txt not found.")
        return ""

def flatten(lst):
    return [item for sublist in lst for item in sublist]

def format_output(bias_result, sentiment_result):
    return {
        "bias_overall": bias_result.get("bias_overall"),
        "sentiment_overall": [s.get("label") for s in sentiment_result],
        "remarks": bias_result.get("remarks"),
        "highlighted_bias_lines": bias_result.get("highlighted_bias_lines"),
    }
