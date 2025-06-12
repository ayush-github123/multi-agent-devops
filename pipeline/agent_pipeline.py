from agents.ticket_agent import classify_ticket
from agents.dev_agent import generate_code
from agents.review_agent import review_code

def run_pipeline(ticket_text):
    print("🕵️ Running TicketAgent...")
    ticket_info = classify_ticket(ticket_text)
    
    print("\n📋 Ticket Classification:")
    for key, value in ticket_info.items():
        print(f"{key.capitalize()}: {value}")

    print("\n💻 Running DevAgent...")
    code_output = generate_code(ticket_info['summary'], ticket_info['category'])

    print("\n📁 File:", code_output['filename'])
    print("\n🧾 Code:\n", code_output['code'])
    print("\n🧠 Explanation:\n", code_output['explanation'])

    print("\n🧪 Running ReviewAgent...")
    review = review_code(code_output["code"])

    print("\n📋 Review:", review['review'])
    print("\n📊 Score:", review['score'])
    print("\n✅ Ready:", review['ready'])

# Example tickets
if __name__ == "__main__":
    # ticket = """App crashes when uploading a PNG image larger than 5MB on the user profile page."""
    # run_pipeline(ticket)

    ticket = """The login page doesn't redirect to the dashboard after successful authentication."""
    run_pipeline(ticket)

    # ticket = """Need to add logging for failed API requests in the payment gateway service."""
    # run_pipeline(ticket)
