import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from agents.ticket_agent import classify_ticket
from agents.dev_agent import generate_code
from agents.review_agent import review_code
from agents.test_agent import generate_tests
from agents.improve_agent import improve_code
from agents.explain_agent import explain_code
from utils.run_test import run_python_tests
from utils.zip_file import create_export_zip 

MAX_ATTEMPTS = 3
REVIEW_THRESHOLD = 7.0

st.set_page_config(page_title="DevPilot", page_icon="🛠️", layout="wide")
st.title("🧠 AI Dev Assistant")
st.write("Enter a user ticket below and watch the agent pipeline work through it step-by-step!")

# Initialize state
if "pipeline_ran" not in st.session_state:
    st.session_state.pipeline_ran = False
if "improved_code" not in st.session_state:
    st.session_state.improved_code = None

ticket_input = st.text_area("🎟️ User Ticket", height=150, placeholder="e.g., Add a Django view to update user profiles...")

# 🚀 RUN PIPELINE
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
        feedback_for_retry = None

        while attempts < MAX_ATTEMPTS:
            with st.spinner(f"💻 Running DevAgent (Attempt {attempts + 1})..."):
                code_output = generate_code(
                    ticket_info['summary'],
                    ticket_info['category'],
                    ticket_info["language"].lower(),
                    feedback_for_retry
                )

            st.subheader(f"📁 Code Output - Attempt {attempts + 1}")
            st.markdown(f"**Filename**: `{code_output['filename']}`")
            st.code(code_output['code'], language=ticket_info["language"].lower())
            st.expander("🧠 Explanation").write(code_output['explanation'])

            with st.spinner("🔍 Running ReviewAgent..."):
                review = review_code(code_output["code"], ticket_info["language"].lower())

            try:
                score = float(review["score"])
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
                    test_results = generate_tests(code_output["code"], ticket_info["language"])

                st.subheader("🧪 Unit Tests")
                if "error" in test_results:
                    st.error("❌ Failed to generate tests.")
                    st.text(test_results["error"])
                    st.code(test_results.get("raw_output", ""), language="markdown")
                else:
                    st.markdown(f"**Framework**: `{test_results['framework']}`")
                    st.code(test_results["test_code"], language=ticket_info["language"].lower())
                    st.expander("💡 What the Tests Cover").write(test_results["explanation"])
                    best_test_output = test_results

                    # if ticket_info["language"].lower() == "python":
                    #     st.subheader("📊 Test Execution Result")
                    #     test_run_result = run_python_tests(best_test_output["test_code"])

                    #     if "error" in test_run_result:
                    #         st.error("❌ Error running test code")
                    #         st.text(test_run_result["error"])
                    #     else:
                    #         st.code(test_run_result["stdout"] or "✅ All tests passed!", language="bash")
                    #         if test_run_result["stderr"]:
                    #             st.error("⚠️ Warnings/Errors:")
                    #             st.code(test_run_result["stderr"], language="bash")

                break

            feedback_for_retry = review.get("review", "")
            st.warning(f"⚠️ Score {score} is below threshold ({REVIEW_THRESHOLD}). Retrying...\n")
            attempts += 1

        # Save pipeline state
        st.session_state.pipeline_ran = True
        st.session_state["ticket_info"] = ticket_info
        st.session_state["best_code_output"] = best_code_output
        st.session_state["best_review"] = best_review
        st.session_state["test_results"] = best_test_output
        st.session_state.improved_code = None  # reset previous improvement

# DISPLAY FINAL OUTPUT AFTER PIPELINE
if st.session_state.get("pipeline_ran", False):
    ticket_info = st.session_state["ticket_info"]
    best_code_output = st.session_state["best_code_output"]
    best_review = st.session_state["best_review"]
    best_test_output = st.session_state.get("test_results", None)

    st.divider()
    st.subheader("📦 Final Output")
    if best_code_output:
        st.markdown(f"**📁 File**: `{best_code_output['filename']}`")
        st.code(best_code_output['code'], language=ticket_info["language"].lower())

    if best_review:
        st.markdown(f"**📊 Final Score**: {best_review['score']}/10")
        st.markdown(f"**✅ Ready for Deployment**: {best_review['ready']}")
        st.expander("🧾 Final Review").write(best_review['review'])

    if best_code_output:
        if st.button("🧠 Explain This Code"):
            with st.spinner("Thinking..."):
                explanation = explain_code(best_code_output['code'])
                st.subheader("📖 Code Explanation")
                st.write(explanation)

    if best_code_output:
        st.divider()
        st.subheader("✍️ Edit & Re-Review")

        edited_code = st.text_area(
            "📝 Modify the generated code (if needed):",
            value=best_code_output['code'],
            height=300,
            key="manual_edit"
        )

        if st.button("🕵️ Re-run ReviewAgent", key="review_button"):
            with st.spinner("Re-reviewing your edited code..."):
                edited_review = review_code(edited_code, ticket_info["language"].lower())

            try:
                new_score = float(edited_review["score"])
            except Exception:
                new_score = 0.0

            st.subheader("📋 New Review (After Edit)")
            st.markdown(f"**Score:** {new_score}/10")
            st.markdown(f"**Ready for Deployment:** {edited_review['ready']}")
            st.expander("💬 Full Review").write(edited_review["review"])


    if best_test_output:
        st.subheader("✅ Final Unit Tests")
        if "error" in best_test_output:
            st.error("❌ Test generation failed.")
            st.text(best_test_output["error"])
            st.code(best_test_output.get("raw_output", ""), language="markdown")
        else:
            st.markdown(f"**Framework**: `{best_test_output['framework']}`")
            st.code(best_test_output["test_code"], language=ticket_info["language"].lower())
            st.expander("💡 What the Tests Cover").write(best_test_output["explanation"])

# IMPROVE CODE SECTION (Always available after pipeline run)
if st.session_state.get("best_code_output") and st.session_state.get("ticket_info"):
    st.divider()
    st.subheader("🧠 Improve your Code")

    feedback = st.text_area("💬 Suggest how to improve the code or review", height=100, key="feedback_area")

    if st.button("🔁 Improve with My Feedback", key="improve_button"):
        with st.spinner("Improving your code..."):
            improved = improve_code(
                st.session_state["best_code_output"]["code"],
                feedback,
                st.session_state["ticket_info"]["language"].lower()
            )
            st.session_state.improved_code = improved

    if st.session_state.improved_code:
        st.subheader("🔧 Code Improved Based on Your Feedback")
        st.code(st.session_state.improved_code, language=st.session_state["ticket_info"]["language"].lower())

        if st.button("🧠 Explain This Code", key="explain_code"):
            with st.spinner("Thinking..."):
                explanation = explain_code(st.session_state.improved_code)
                st.subheader("📖 Improved Code Explanation")
                st.write(explanation)


    #Export to ZIP File
    if best_code_output:
        st.divider()
        st.subheader("📦 Export Final Output")

        export_code    = best_code_output["code"]
        export_fname   = best_code_output["filename"]
        print(export_fname)
        export_tests   = best_test_output.get("test_code") if best_test_output else None
        export_review  = best_review["review"] if best_review else None
        export_impcode = st.session_state.get("improved_code", None)   

        zip_bytes = create_export_zip(
            code          = export_code,
            filename      = export_fname,
            test_code     = export_tests,
            review        = export_review,
            improved_code = export_impcode,
            language      = ticket_info["language"]
        )

        st.download_button(
            label      = "⬇️ Download ZIP",
            data       = zip_bytes,
            file_name  = "devpilot_output.zip",
            mime       = "application/zip"
        )
