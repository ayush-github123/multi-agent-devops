from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

IMPROVE_PROMPT = PromptTemplate.from_template("""
You are a senior software engineer. Your task is to improve the following {language} code based on a reviewer's feedback.

--- CODE TO IMPROVE ---
```{language}
{code}
--- REVIEWER FEEDBACK ---
{feedback}

Instructions:

Improve the code based on the feedback.

Return only the improved code followed by bullet points listing what was improved.

Do not use markdown syntax (no triple backticks, no headings).

Keep explanations minimal and directly tied to changes.
""")

def improve_code(code: str, feedback: str, language: str) -> str:
    """
    Improve code based on reviewer feedback.
    Returns:
        Improved code with bullet-point improvements.
        Returns error message string on failure.
    """
    try:
        chain = IMPROVE_PROMPT | llm
        result = chain.invoke({"code": code, "feedback": feedback, "language": language})
        content = result.content.strip()
        print(content)

        # Remove triple backticks and language labels if any slipped through
        cleaned = content.replace("```", "").replace(language, "").strip()

        return cleaned

    except Exception as e:
        return f"# Error during improvement: {str(e)}"
