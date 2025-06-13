from agents.ticket_agent import classify_ticket
from agents.dev_agent import generate_code
from agents.review_agent import review_code

MAX_ATTEMPTS = 3
REVIEW_THRESHOLD = 7.0

def orchestrate_pipeline(user_ticket: str):
    print("📨 User Ticket Received")
    print(f"📝 {user_ticket}\n")

    print("🕵️ Running TicketAgent...")
    ticket_info = classify_ticket(user_ticket)

    print("\n📋 Ticket Classification:")
    for key, value in ticket_info.items():
        print(f"{key.capitalize()}: {value}")

    attempts = 0
    best_score = 0.0
    best_review = None
    best_code_output = None

    while attempts < MAX_ATTEMPTS:
        print(f"\n💻 Running DevAgent... (Attempt {attempts + 1})")
        code_output = generate_code(ticket_info['summary'], ticket_info['category'])

        print("\n📁 File:", code_output['filename'])
        print("\n🧾 Code:\n", code_output['code'])
        print("\n🧠 Explanation:\n", code_output['explanation'])

        print("\n🧪 Running ReviewAgent...")
        review = review_code(code_output["code"])
        score = review["score"]

        print("\n📋 Review:", review['review'])
        print("📊 Score:", score)
        print("✅ Ready:", review['ready'])

        if score > best_score:
            best_score = score
            best_review = review
            best_code_output = code_output

        if score >= REVIEW_THRESHOLD:
            print("\n🎉 Code passed the review threshold!")
            break

        print(f"\n⚠️ Score {score} is below threshold ({REVIEW_THRESHOLD}). Retrying...\n")
        attempts += 1

    if best_score < REVIEW_THRESHOLD:
        print(f"\n❌ Max attempts reached. Best score achieved: {best_score}")

    print("\n📦 Final Output:")
    print("📁 File:", best_code_output['filename'])
    print("🧾 Code:\n", best_code_output['code'])
    print("📋 Final Review:", best_review['review'])
    print("📊 Final Score:", best_score)
    print("✅ Ready Status:", best_review['ready'])

# Example ticket
if __name__ == "__main__":
    # ticket = """App crashes when uploading a PNG image larger than 5MB on the user profile page."""
    # orchestrate_pipeline(ticket)

    # ticket = """Login page doesn't redirect to the dashboard after successful authentication."""
    # orchestrate_pipeline(ticket)

    # ticket = """Add retry logic and logging for failed API requests in the payment gateway service."""
    # orchestrate_pipeline(ticket)

    # ticket = """The system crashes due to running out of RAM during the data preprocessing stage."""
    # orchestrate_pipeline(ticket)

    ticket = """Add a new Django view to handle user profile updates, including name, bio, and profile picture upload. Ensure proper form validation and handle image upload to the media directory."""
    orchestrate_pipeline(ticket)
