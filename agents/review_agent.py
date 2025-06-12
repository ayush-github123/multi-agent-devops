from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)


REVIEW_PROMPT = PromptTemplate.from_template("""
You are a senior Python code reviewer. Review the following code snippet and do the following:
1. Identify any bugs or syntax errors.
2. Suggest improvements or optimizations.
3. Give a score out of 10 for code quality.
4. Mention whether the code is ready for deployment or needs changes.

CODE:
```python
{code}
                                             
FORMAT:
Review:

<your comments>
Score: <score>/10
Ready for deployment: Yes/No
""")

def review_code(code: str) -> dict:
    chain = REVIEW_PROMPT | llm
    response = chain.invoke({"code": code})
    lines = response.content.strip().splitlines()
    review_lines = [line for line in lines if not line.startswith("Score") and not line.startswith("Ready")]

    score = next((line.split(":")[1].strip() for line in lines if line.startswith("Score")), "N/A")
    ready = next((line.split(":")[1].strip() for line in lines if line.startswith("Ready")), "N/A")

    return {
        "review": "\n".join(review_lines),
        "score": score,
        "ready": ready
    }