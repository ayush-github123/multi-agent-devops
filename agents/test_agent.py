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
You are a senior software developer. Given the following code in {language}, generate 1–3 unit tests using the standard testing framework for that language.

CODE:
```{language}
{code}
```
Requirements:

Choose the correct test framework (e.g., pytest/unittest for Python, Jest for JavaScript/React, JUnit for Java, etc.).
Also return a suitable filename according to the framework used.

Output realistic, meaningful tests for actual behavior.

Format:

---FRAMEWORK---
<framework name>

---TEST CODE---
<test code>

---EXPLANATION---
<brief explanation of what the tests validate>

""")

def generate_tests(code: str, language: str) -> dict:
    try:
        chain = TEST_PROMPT | llm
        response = chain.invoke({"code": code, "language": language})
        content = response.content.strip()

        framework = content.split("---FRAMEWORK---")[1].split("---")[0].strip()
        test_code = content.split("---TEST CODE---")[1].split("---")[0].strip()
        explanation = content.split("---EXPLANATION---")[1].strip()

        cleaned_code = test_code
        if cleaned_code.startswith("```"):
            cleaned_code = cleaned_code.strip("`").split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        return {
            "framework": framework,
            "test_code": cleaned_code,
            "explanation": explanation
        }


    except Exception as e:
        return {
            "error": str(e),
            "raw_output": content if "content" in locals() else ""
        }
