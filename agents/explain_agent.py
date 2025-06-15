from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

EXPLAIN_PROMPT = PromptTemplate.from_template("""
You are an expert Python developer. Explain the following Python code in a clear and beginner-friendly way.

- Go line-by-line if possible.
- Avoid complex jargon.
- Use bullet points or markdown formatting.
- Make the explanation educational and helpful.

Code:
```python
{code}
""")

def explain_code(code: str):
    chain = EXPLAIN_PROMPT | llm
    response = chain.invoke({"code": code})
    return response.content.strip()


