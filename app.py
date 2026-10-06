import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq


# =========================================================
# SETUP
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎤",
    layout="centered"
)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is missing. Please check your .env file.")
    st.stop()

client = Groq(api_key=api_key)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mock_started" not in st.session_state:
    st.session_state.mock_started = False

if "current_question" not in st.session_state:
    st.session_state.current_question = ""


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎯 Interview Coach")

mode = st.sidebar.selectbox(
    "Choose Mode",
    [
        "💬 Normal Chat",
        "🎤 Mock Interview"
    ]
)

category = st.sidebar.selectbox(
    "Interview Category",
    [
        "General",
        "Python",
        "C",
        "Java",
        "DBMS",
        "SQL",
        "DSA",
        "AI / ML",
        "HTML / CSS",
        "Computer Networks",
        "Operating Systems",
        "HR"
    ]
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    [
        "Easy",
        "Medium",
        "Hard"
    ]
)


# =========================================================
# CLEAR CHAT
# =========================================================

if st.sidebar.button("🗑️ Clear Chat"):

    st.session_state.messages = []
    st.session_state.mock_started = False
    st.session_state.current_question = ""

    st.rerun()


# =========================================================
# TITLE
# =========================================================

st.title("🎤 AI Interview Coach")

st.caption(
    "Your AI assistant for technical and HR interview preparation."
)


# =========================================================
# NORMAL CHAT
# =========================================================

if mode == "💬 Normal Chat":

    st.info(
        f"📚 Category: {category}  |  📊 Difficulty: {difficulty}"
    )

    # Display previous messages
    for message in st.session_state.messages:

        if message["role"] == "user":
            avatar = "🧑‍💻"
        else:
            avatar = "🤖"

        with st.chat_message(
            message["role"],
            avatar=avatar
        ):
            st.write(message["content"])


    question = st.chat_input(
        "Ask any interview question..."
    )


    if question:

        # Show user question
        with st.chat_message(
            "user",
            avatar="🧑‍💻"
        ):
            st.write(question)

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # System prompt
        system_prompt = f"""
You are an AI Interview Coach.

Help the student prepare for interviews.

Interview Category:
{category}

Difficulty:
{difficulty}

You can answer questions about:
Python, C, Java, DBMS, SQL, DSA,
AI/ML, HTML/CSS, Computer Networks,
Operating Systems and HR interviews.

Give clear and beginner-friendly answers.

Use simple examples when useful.

For interview questions, provide answers
that a student can confidently use in an interview.
"""


        # Prepare conversation
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        messages.extend(
            st.session_state.messages
        )


        # Generate response
        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            with st.spinner("🤔 Thinking..."):

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=messages,
                    temperature=0.5,
                    max_tokens=700
                )

                answer = response.choices[0].message.content

            st.write(answer)


        # Save answer
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# =========================================================
# MOCK INTERVIEW
# =========================================================

elif mode == "🎤 Mock Interview":

    st.info(
        f"🎯 {category} Mock Interview  |  📊 {difficulty}"
    )


    # -----------------------------------------------------
    # START INTERVIEW
    # -----------------------------------------------------

    if not st.session_state.mock_started:

        st.write(
            "The AI will ask you one question at a time."
        )

        if st.button("🚀 Start Mock Interview"):

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "system",
                        "content": f"""
You are a professional interviewer.

Conduct a {category} interview.

Difficulty:
{difficulty}

Ask ONE interview question.

Do not give the answer.

Keep the question suitable for
a BTech student preparing for placements.
"""
                    },
                    {
                        "role": "user",
                        "content": "Start the interview."
                    }
                ],

                temperature=0.5,
                max_tokens=300
            )

            question = response.choices[0].message.content

            st.session_state.current_question = question

            st.session_state.mock_started = True

            st.rerun()


    # -----------------------------------------------------
    # CONTINUE INTERVIEW
    # -----------------------------------------------------

    else:

        st.subheader("🎤 Interview Question")

        st.write(
            st.session_state.current_question
        )


        answer = st.chat_input(
            "Type your answer..."
        )


        if answer:

            # Show candidate answer
            with st.chat_message(
                "user",
                avatar="🧑‍💻"
            ):
                st.write(answer)


            # Ask AI to evaluate and continue
            with st.spinner(
                "🤔 Evaluating your answer..."
            ):

                response = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "system",
                            "content": f"""
You are conducting a professional
{category} interview.

Difficulty:
{difficulty}

Evaluate the candidate's answer.

Give:

⭐ Score: X/10

✅ What was good:
- Mention important strengths.

⚠️ What can be improved:
- Mention important improvements.

💡 Better Answer:
Give a short interview-ready answer.

Then ask ONE new interview question.

Do not ask multiple questions.
"""
                        },

                        {
                            "role": "user",
                            "content": f"""
Interview Question:

{st.session_state.current_question}


Candidate Answer:

{answer}
"""
                        }
                    ],

                    temperature=0.5,
                    max_tokens=700
                )

                feedback = response.choices[0].message.content


            # Display feedback
            with st.chat_message(
                "assistant",
                avatar="🤖"
            ):
                st.write(feedback)


            # Save the latest question/feedback
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": answer
                }
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": feedback
                }
            )


            # Generate next question separately
            next_question_response = client.chat.completions.create(

                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "system",
                        "content": f"""
You are an interviewer conducting
a {category} interview.

Difficulty:
{difficulty}

Ask ONE new interview question.

Return ONLY the question.
Do not provide the answer.
"""
                    },
                    {
                        "role": "user",
                        "content": "Ask the next interview question."
                    }
                ],

                temperature=0.5,
                max_tokens=200
            )

            next_question = (
                next_question_response
                .choices[0]
                .message
                .content
            )

            st.session_state.current_question = next_question

            st.rerun()