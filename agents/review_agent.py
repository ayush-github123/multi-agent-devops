from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import re, os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
)

REVIEW_PROMPT = PromptTemplate.from_template(
    """You are a senior {language} code reviewer.

Analyse the code below and provide **all** of the following:

1. A short review summarising any issues, bugs, or improvements.
2. A list of specific suggested changes (if any).
3. A quality rating **out of 10** (higher = better).
4. **Ready for deployment?**  
   • Return **exactly** “Yes” if there are **no critical bugs or minute(ignorable) bugs and quality ≥ 8**.  
   • Return “No” otherwise.

### CODE
```{language}
{code}
```
FORMAT (STRICT)
Review:
<your comments here>

Score: <number>/10
Ready for deployment: Yes|No
"""
)

def review_code(code: str, language:str) -> dict:
    """Return dict with keys: review, score (float), ready ('Yes'|'No')."""
    response = (REVIEW_PROMPT | llm).invoke({"code": code, "language":language})
    content = response.content.strip()

    score_match = re.search(r"Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10", content, re.I)
    score = float(score_match.group(1)) if score_match else 0.0

    ready_match = re.search(r"Ready\s*for\s*deployment:\s*(Yes|No)\b", content, re.I)
    if ready_match:
        ready = ready_match.group(1).capitalize()
    else:
        # Fallback: infer from score threshold 8.0
        ready = "Yes" if score >= 8.0 else "No"

    cleaned_lines = [
        ln for ln in content.splitlines()
        if not re.match(r"\s*Score:", ln, re.I)
        and not re.match(r"\s*Ready\s*for\s*deployment:", ln, re.I)
        and ln.strip()  # keep non‑empty
    ]
    review_text = "\n".join(cleaned_lines).strip()

    return {
        "review": review_text,
        "score":  score,
        "ready":  ready
    }