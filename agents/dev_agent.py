from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load GEMINI API key
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# Improved Prompt Template
DEV_PROMPT = PromptTemplate.from_template("""
You are an expert software engineer proficient in multiple programming languages.
Given a software development ticket, your job is to write clean, efficient, and minimal code to solve the problem or implement the feature.

---TICKET SUMMARY---
{summary}

---CATEGORY---
{category}

---LANGUAGE---
{language}

Instructions:
1. Return only a single code file in the specified language.
2. Focus on core logic only. Do not include setup, scaffolding, or unnecessary boilerplate.
3. Add helpful inline comments to explain the logic.
4. After the code, include a short paragraph explaining what the code does.

Format your output strictly like this:

---FILENAME---
<filename.ext>
---CODE---
<code here>
---EXPLANATION---
<brief explanation of what this code does>

Make sure your response is parsable using the above format.
""")

def generate_code(summary: str, category: str, language: str = "Python") -> dict:
    """
    Generates code based on a ticket summary, category, and programming language.
    Returns structured output with filename, code, and explanation.
    """
    chain = DEV_PROMPT | llm
    response = chain.invoke({
        "summary": summary,
        "category": category,
        "language": language,
    })

    content = response.content.strip()
    result = {"language": language}

    # Parsing the structured output
    try:
        filename = content.split("---FILENAME---")[1].split("---")[1].strip()
        code = content.split("---CODE---")[1].split("---")[0].strip()
        explanation = content.split("---EXPLANATION---")[1].strip()

        result.update({
            "filename": filename,
            "code": code,
            "explanation": explanation
        })

    except Exception as e:
        result["error"] = f"Failed to parse LLM output: {str(e)}"
        result["raw"] = content

    return result

# Example Usage
if __name__ == "__main__":
    ticket = "Add a search bar to filter products by name on the homepage."
    category = "feature"
    language = "JavaScript"

    output = generate_code(ticket, category, language)
    
    if "error" in output:
        print("Error:", output["error"])
        print("Raw Output:", output["raw"])
    else:
        print(f"File: {output['filename']}")
        print("----- Code -----")
        print(output["code"])
        print("----- Explanation -----")
        print(output["explanation"])
