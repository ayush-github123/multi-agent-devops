from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv


load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

TICKET_PROMPT = PromptTemplate.from_template("""
You are a helpful engineering assistant. Analyze the following software development issue or feature request.

TASKS:
1. Classify the ticket as one of the following categories: [Bug, Feature, Documentation, Enhancement].
2. Rate its urgency as one of: [Low, Medium, High, Critical].
3. Identify the programming language being referred to in the ticket (e.g., Python, JavaScript, Java, etc.). If no specific language is mentioned, return "Unknown".
4. Generate a short summary (1–2 lines) of the ticket.

TICKET:
{ticket_text}

FORMAT:
Category: <one-word>
Urgency: <one-word>
Language: <one-word>
Summary: <summary here>
""")



def classify_ticket(ticket_text: str) -> dict:
    chain = TICKET_PROMPT | llm
    response = chain.invoke({"ticket_text":ticket_text})

    result={}
    for line in response.content.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip().lower()] = value.strip()
    
    return result


# # Example usage
# if __name__ == "__main__":
#         # ticket = """App crashes when uploading a PNG image larger than 5MB on the user profile page."""
#     ticket = """Website Login Failure"""
#     print(classify_ticket(ticket))


