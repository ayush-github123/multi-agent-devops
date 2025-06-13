from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv


load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

IMPROVE_PROMPT = PromptTemplate.from_template("""
You are a senior software engineer. Your task is to improve the following Python code based on a reviewer's feedback.

--- CODE TO IMPROVE ---
```python
{code}
--- REVIEWER FEEDBACK ---
{feedback}

Please return only the improved Python code and then mention the points you have improved.(no huge explanations or markdown).
""")

def improve_code(code: str, feedback: str) -> str:
    try:
        chain = IMPROVE_PROMPT | llm
        result = chain.invoke({"code": code, "feedback": feedback})
        return result.content.strip()
    except Exception as e:
        return f"# Error during improvement: {str(e)}"

