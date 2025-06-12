from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load GEMINI key
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# Prompt for code generation
DEV_PROMPT = PromptTemplate.from_template("""
You are a professional backend developer. Based on the following ticket summary, generate a Python code file that addresses the feature or bug described.

SUMMARY: {summary}
CATEGORY: {category}

Requirements:
- Generate only Python code.
- Keep it short and minimal — just the core logic.
- Add comments in the code.
- Also provide a short explanation of what the code does.

FORMAT:
---FILENAME---
<filename.py>
---CODE---
<code here>
---EXPLANATION---
<what it does>
""")

def generate_code(summary: str, category: str) -> dict:
    chain = DEV_PROMPT | llm
    response = chain.invoke({"summary": summary, "category": category})

    content = response.content.strip()
    result = {"language": "Python"}
    
    # Simple parsing
    try:
        filename = content.split("---FILENAME---")[1].split("---")[1].strip()
        code = content.split("---CODE---")[1].split("---")[0].strip()
        explanation = content.split("---EXPLANATION---")[1].strip()

        result["filename"] = filename
        result["code"] = code
        result["explanation"] = explanation
    except Exception as e:
        result["error"] = f"Failed to parse LLM output: {str(e)}"
        result["raw"] = content

    return result

# Example usage
# if __name__ == "__main__":
    # ticket = """App crashes when uploading a PNG image larger than 5MB on the user profile page."""
    # result = classify_ticket(ticket_text=ticket)
    # summary = result["summary"]
    # category = result["category"]
    # output = generate_code(summary, category)
    
    # print(f"File: {output['filename']}")
    # print("----- Code -----")
    # print(output["code"])
    # print("----- Explanation -----")
    # print(output["explanation"])