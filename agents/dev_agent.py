from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os, re

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

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
1. Return only a single code file in {language}.
2. Focus on core logic only. Do not include setup, scaffolding, or unnecessary boilerplate.
3. Add helpful inline comments to explain the logic.
4. After the code, include a short paragraph explaining what the code does.
5. Return the filename with it's respective extension according to the programming language used in code.

Format your output strictly like this:

---FILENAME---
<filename.extension>
---CODE---
<code here>
---EXPLANATION---
<brief explanation of what this code does>

Make sure your response is parsable using the above format.
""")

def generate_code(summary: str, category: str, language: str, feedback: str=None) -> dict:
    """
    Generates code based on a ticket summary, category, and programming language.
    Returns structured output with filename, code, and explanation.
    """
    dev_prompt = DEV_PROMPT.template
    if feedback:
        dev_prompt = PromptTemplate.from_template(dev_prompt + f"\nPrevious feedback to improve on:\n{feedback}")
        chain = dev_prompt | llm
    else:
        chain = DEV_PROMPT | llm
        
    response = chain.invoke({
        "summary": summary,
        "category": category,
        "language": language
    })

    content = response.content.strip()
    result = {"language": language}

    # Parsing the structured output
    try:
        match = re.search(
                r"---FILENAME---\s*(.+?)\s*---CODE---\s*(.+?)\s*---EXPLANATION---\s*(.+)", 
                content, 
                re.DOTALL
            )

        if match:
            filename = match.group(1).strip()
            code = match.group(2).strip()
            explanation = match.group(3).strip()

        result.update({
            "filename": filename,
            "code": code,
            "explanation": explanation
        })

    except Exception as e:
        result["error"] = f"Failed to parse LLM output: {str(e)}"
        result["raw"] = content

    return result