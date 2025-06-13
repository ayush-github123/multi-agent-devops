from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Load model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# Prompt
TEST_PROMPT = PromptTemplate.from_template("""
You are a senior Python developer. Given the following Python code, generate 1–3 unit tests using either `unittest` or `pytest`.

CODE:
```python
{code}
Requirements:

Choose between unittest or pytest, and mention it

Tests must be realistic and reflect actual function behavior

Output the result in this format:

---FRAMEWORK---
unittest OR pytest

---TEST CODE---
<actual test code here>

---EXPLANATION---
<short explanation of what the tests cover>
""")

def generate_tests(code: str) -> dict:
    try:
        chain = TEST_PROMPT | llm
        response = chain.invoke({"code": code})
        content = response.content.strip()
        
        # Parse response
        framework = content.split("---FRAMEWORK---")[1].split("---")[0].strip()
        test_code = content.split("---TEST CODE---")[1].split("---")[0].strip()
        explanation = content.split("---EXPLANATION---")[1].strip()

        return {
            "framework": framework,
            "test_code": test_code,
            "explanation": explanation
        }

    except Exception as e:
        return {
            "error": str(e),
            "raw_output": content if "content" in locals() else ""
        }