import streamlit as st

from orchestrator import run_orchestrator
from output_formatter import format_response


st.set_page_config(
    page_title="Kohler Unified Enterprise AI Agent",
    page_icon="🌸",
    layout="centered",
)

st.markdown(
    """
    <style>
    :root {
        --blush: #fff4f5;
        --rose: #d94f78;
        --rose-deep: #a8325b;
        --rose-muted: #a66d7d;
        --ink: #402832;
        --cream: #fffdfb;
        --line: #f1d5dc;
    }

    .stApp {
        background: linear-gradient(145deg, #fff8f8 0%, #ffe9ee 52%, #fff4ef 100%);
        color: var(--ink);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 820px;
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 1.4rem 0 1.8rem;
        text-align: center;
    }

    .hero h1 {
        margin: 0;
        background: linear-gradient(90deg, #a8325b, #e75480, #bb5270);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: 0;
    }

    .hero p {
        margin: 0.6rem 0 0;
        color: var(--rose-muted);
        font-size: 1rem;
    }

    [data-testid="stChatMessage"] {
        border-radius: 22px;
        margin: 0.75rem 0;
        padding: 0.85rem 1rem;
        box-shadow: 0 7px 22px rgba(143, 63, 88, 0.08);
        border: 1px solid var(--line);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #eaa0b5;
        color: #351d27;
        margin-left: 12%;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: rgba(255, 253, 251, 0.94);
        color: var(--ink);
        margin-right: 12%;
    }

    [data-testid="stChatMessage"] p {
        color: inherit;
    }

    .domain-badge {
        display: inline-block;
        margin: 0 0 0.45rem;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        color: #542d3b;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    .domain-hr { background: #f7c4d2; }
    .domain-support { background: #ded2f5; }
    .domain-privacy { background: #ffd8bd; }
    .domain-unknown { background: #eadfe2; }

    div.stButton > button {
        min-height: 2.35rem;
        border: 1px solid #efb7c5;
        border-radius: 999px;
        background: rgba(255, 253, 251, 0.8);
        color: var(--rose-deep);
        font-size: 0.78rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(143, 63, 88, 0.06);
    }

    div.stButton > button:hover {
        border-color: var(--rose);
        background: #ffe0e7;
        color: #7f2446;
    }

    [data-testid="stChatInput"] {
        border-color: #e6a7b8;
        border-radius: 22px;
        background: rgba(255, 253, 251, 0.92);
        box-shadow: 0 8px 26px rgba(143, 63, 88, 0.12);
    }

    [data-testid="stChatInput"] textarea {
        color: var(--ink);
    }

    .examples-label {
        margin: 1.5rem 0 0.55rem;
        color: var(--rose-muted);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🌸 Kohler Unified Enterprise AI Agent</h1>
        <p>Ask about HR Policy, Customer Support, or Privacy Policy</p>
    </div>
    """,
    unsafe_allow_html=True,
)


if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


for message in st.session_state.conversation_history:
    role = message["role"]
    avatar = "🌸" if role == "assistant" else "🪷"
    with st.chat_message(role, avatar=avatar):
        if role == "assistant":
            domain = message.get("domain", "unknown")
            domain_label = {
                "hr_policy": "HR",
                "customer_support": "Support",
                "privacy_policy": "Privacy",
            }.get(domain, "Unknown")
            domain_class = {
                "hr_policy": "domain-hr",
                "customer_support": "domain-support",
                "privacy_policy": "domain-privacy",
            }.get(domain, "domain-unknown")
            st.markdown(
                f'<span class="domain-badge {domain_class}">{domain_label}</span>',
                unsafe_allow_html=True,
            )
        st.markdown(message["content"])


st.markdown('<div class="examples-label">Try asking</div>', unsafe_allow_html=True)
example_columns = st.columns(3)
example_questions = (
    "How many leave days do I get?",
    "What's your return policy?",
    "How is my data used?",
)
selected_example = None
for column, example in zip(example_columns, example_questions):
    with column:
        if st.button(example, use_container_width=True):
            st.session_state.prompt_input = example
            st.rerun()

with st.form("chat_form", clear_on_submit=True, border=False):
    user_message = st.text_input(
        "Ask a question...",
        key="prompt_input",
        label_visibility="collapsed",
        placeholder="Ask a question...",
    )
    submitted = st.form_submit_button("Send  ✦", use_container_width=True)

user_message = user_message if submitted else None
if user_message:
    with st.chat_message("user", avatar="🪷"):
        st.markdown(user_message)

    try:
        with st.spinner("Thinking... 🌸"):
            result = run_orchestrator(
                current_message=user_message,
                conversation_history=st.session_state.conversation_history,
            )
        confidence = max(
            (chunk.similarity_score for chunk in result.retrieved_chunks),
            default=0.0,
        )
        formatted_answer = format_response(
            user_message=user_message,
            answer=result.answer,
            source_domain=result.domain,
            confidence=confidence,
        )
    except Exception as error:
        formatted_answer = f"Sorry, I couldn't process that request: {error}"
        result = None

    with st.chat_message("assistant", avatar="🌸"):
        domain_label = {
            "hr_policy": "HR",
            "customer_support": "Support",
            "privacy_policy": "Privacy",
        }.get(result.domain if result else "unknown", "Unknown")
        domain_class = {
            "hr_policy": "domain-hr",
            "customer_support": "domain-support",
            "privacy_policy": "domain-privacy",
        }.get(result.domain if result else "unknown", "domain-unknown")
        st.markdown(
            f'<span class="domain-badge {domain_class}">{domain_label}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(formatted_answer)

    st.session_state.conversation_history.append(
        {
            "role": "user",
            "content": user_message,
            "domain": result.domain if result else "unknown",
        }
    )
    st.session_state.conversation_history.append(
        {
            "role": "assistant",
            "content": formatted_answer,
            "domain": result.domain if result else "unknown",
        }
    )