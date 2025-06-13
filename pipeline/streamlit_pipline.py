import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from agents.ticket_agent import classify_ticket
from agents.dev_agent import generate_code
from agents.review_agent import review_code
from agents.test_agent import generate_tests

MAX_ATTEMPTS = 3
REVIEW_THRESHOLD = 7.0

st.set_page_config(page_title="DevPilot", page_icon="🛠️", layout="wide")
st.title("🧠 AI Dev Assistant")
st.write("Enter a user ticket below and watch the agent pipeline work through it step-by-step!")

ticket_input = st.text_area("🎟️ User Ticket", height=150, placeholder="e.g., Add a Django view to update user profiles...")

if st.button("🚀 Run Pipeline"):
    if not ticket_input.strip():
        st.warning("Please enter a ticket before running.")
    else:
        st.success("📨 Ticket received!")
        st.code(ticket_input, language="markdown")

        with st.spinner("🕵️ Running TicketAgent..."):
            ticket_info = classify_ticket(ticket_input)
            st.subheader("📋 Ticket Classification")
            st.json(ticket_info)

        attempts = 0
        best_score = 0.0
        best_review = None
        best_code_output = None
        best_test_output = None

        while attempts < MAX_ATTEMPTS:
            with st.spinner(f"💻 Running DevAgent (Attempt {attempts + 1})..."):
                code_output = generate_code(ticket_info['summary'], ticket_info['category'])

            st.subheader(f"📁 Code Output - Attempt {attempts + 1}")
            st.markdown(f"**Filename**: `{code_output['filename']}`")
            st.code(code_output['code'], language="python")
            st.expander("🧠 Explanation").write(code_output['explanation'])

            with st.spinner("🔍 Running ReviewAgent..."):
                review = review_code(code_output["code"])

            try:
                score = float(review["score"])
                print(score)
            except (ValueError, TypeError):
                st.warning(f"⚠️ Invalid score format: {review['score']}. Defaulting to 0.0")
                score = 0.0

            st.subheader(f"📋 Review - Attempt {attempts + 1}")
            st.markdown(f"**Score:** {score}/10")
            st.markdown(f"**Ready for Deployment:** {review['ready']}")
            st.expander("💬 Full Review").write(review['review'])

            if score > best_score:
                best_score = score
                best_review = review
                best_code_output = code_output

            if score >= REVIEW_THRESHOLD:
                st.success("🎉 Code passed the review threshold!")

                with st.spinner("🧪 Generating Test Cases..."):
                    test_results = generate_tests(code_output["code"])

                st.subheader("🧪 Unit Tests")
                if "error" in test_results:
                    st.error("❌ Failed to generate tests.")
                    st.text(test_results["error"])
                    st.code(test_results.get("raw_output", ""), language="markdown")
                else:
                    st.markdown(f"**Framework**: `{test_results['framework']}`")
                    st.code(test_results["test_code"], language="python")
                    st.expander("💡 Explanation").write(test_results["explanation"])
                    best_test_output = test_results
                break

            st.warning(f"⚠️ Score {score} is below threshold ({REVIEW_THRESHOLD}). Retrying...\n")
            attempts += 1

        st.divider()
        st.subheader("📦 Final Output")
        if best_code_output:
            st.markdown(f"**📁 File**: `{best_code_output['filename']}`")
            st.code(best_code_output['code'], language="python")

        if best_review:
            st.markdown(f"**📊 Final Score**: {best_score}/10")
            st.markdown(f"**✅ Ready for Deployment**: {best_review['ready']}")
            st.expander("🧾 Final Review").write(best_review['review'])

        # if best_code_output and best_review and best_review["ready"].lower() == "yes" and not best_test_output:
        if best_code_output and best_review and not best_test_output:
            with st.spinner("🧪 Final Test Case Generation..."):
                test_results = generate_tests(best_code_output["code"])

            st.subheader("✅ Final Unit Tests")
            if "error" in test_results:
                st.error("❌ Test generation failed.")
                st.text(test_results["error"])
                st.code(test_results.get("raw_output", ""), language="markdown")
            else:
                st.markdown(f"**Framework**: `{test_results['framework']}`")
                st.code(test_results["test_code"], language="python")
                st.expander("💡 What the Tests Cover").write(test_results["explanation"])
