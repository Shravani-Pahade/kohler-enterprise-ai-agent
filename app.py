import streamlit as st

from document_loader import DOMAINS
from orchestrator import run_orchestrator
from output_formatter import detect_output_format, format_response
from vector_store import build_vector_store, get_chroma_client


st.set_page_config(
    page_title="Kohler Unified Enterprise AI Agent",
    page_icon="K",
    layout="centered",
)


@st.cache_resource(show_spinner=False)
def ensure_knowledge_base() -> dict[str, int]:
    """Build the local ChromaDB collections once when they are missing."""
    client = get_chroma_client()
    collections = {collection.name: collection for collection in client.list_collections()}
    knowledge_base_ready = all(
        domain in collections and collections[domain].count() > 0
        for domain in DOMAINS
    )
    if not knowledge_base_ready:
        with st.spinner("Setting up knowledge base for the first time..."):
            collections = build_vector_store()

    return {domain: collections[domain].count() for domain in DOMAINS}


ensure_knowledge_base()

st.markdown(
    """
    <style>
    :root {
        --white: #ffffff;
        --black: #1a1a1a;
        --maroon: #8c1d24;
        --maroon-dark: #70171d;
        --taupe: #ede7dd;
        --grey: #d9d9d9;
        --muted: #666666;
    }

    .stApp {
        background: var(--white);
        color: var(--black);
    }

    [data-testid="stHeader"] {
        background: var(--white);
        border-bottom: 1px solid var(--grey);
    }

    [data-testid="stToolbar"] {
        color: var(--black);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 900px;
        padding-top: 1.25rem;
        padding-bottom: 2rem;
    }

    .hero {
        margin: -1.25rem -2rem 1.8rem;
        padding: 1.35rem 2rem 1.15rem;
        background: var(--white);
        border-bottom: 4px solid var(--maroon);
        text-align: center;
    }

    .hero .brand {
        color: var(--black);
        font-family: Georgia, serif;
        font-size: 0.68rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }

    .hero h1 {
        margin: 0;
        color: var(--black);
        font-family: Georgia, serif;
        font-size: 2rem;
        font-weight: 400;
        letter-spacing: 0;
    }

    .hero p {
        margin: 0.6rem 0 0;
        color: var(--muted);
        font-size: 1rem;
    }

    [data-testid="stChatMessage"] {
        border-radius: 22px;
        margin: 0.75rem 0;
        padding: 0.85rem 1rem;
        box-shadow: 0 5px 18px rgba(26, 26, 26, 0.06);
        border: 1px solid var(--grey);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: var(--taupe);
        color: var(--black);
        margin-left: 12%;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: var(--white);
        color: var(--black);
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
        color: var(--white);
        background: var(--maroon);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    .domain-hr,
    .domain-support,
    .domain-privacy,
    .domain-financial,
    .domain-legal,
    .domain-unknown { background: var(--maroon); }

    div.stButton > button {
        min-height: 2.35rem;
        border: 1px solid var(--maroon);
        border-radius: 999px;
        background: var(--maroon);
        color: var(--white);
        font-size: 0.78rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(26, 26, 26, 0.08);
    }

    div.stButton > button:hover {
        border-color: var(--maroon-dark);
        background: var(--maroon-dark);
        color: var(--white);
    }

    [data-testid="stForm"] {
        border: 1px solid var(--grey);
        border-radius: 18px;
        background: var(--white);
        padding: 0.35rem;
        box-shadow: 0 8px 26px rgba(26, 26, 26, 0.08);
    }

    [data-testid="stTextInput"] input {
        border-color: var(--grey);
        border-radius: 22px;
        background: var(--white);
        color: var(--black);
    }

    [data-testid="stFormSubmitButton"] button {
        border-radius: 999px;
        border-color: var(--maroon);
        background: var(--maroon);
        color: var(--white);
    }

    [data-testid="stFormSubmitButton"] button:hover {
        border-color: var(--maroon-dark);
        background: var(--maroon-dark);
        color: var(--white);
    }

    .examples-label {
        margin: 1.5rem 0 0.55rem;
        color: var(--muted);
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
        <div class="brand">The Kohler Enterprise Concierge</div>
        <h1>Kohler Unified Enterprise AI Agent</h1>
        <p>Ask about HR Policy, Customer Support, Privacy Policy, Financial Guidelines, or Legal Compliance</p>
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
                "financial_guidelines": "Financial",
                "legal_compliance": "Legal / Compliance",
            }.get(domain, "Unknown")
            domain_class = {
                "hr_policy": "domain-hr",
                "customer_support": "domain-support",
                "privacy_policy": "domain-privacy",
                "financial_guidelines": "domain-financial",
                "legal_compliance": "domain-legal",
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
        with st.spinner("Thinking..."):
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
        output_format = detect_output_format(user_message)
    except Exception as error:
        formatted_answer = f"Sorry, I couldn't process that request: {error}"
        output_format = "markdown"
        result = None

    with st.chat_message("assistant", avatar="🌸"):
        domain_label = {
            "hr_policy": "HR",
            "customer_support": "Support",
            "privacy_policy": "Privacy",
            "financial_guidelines": "Financial",
            "legal_compliance": "Legal / Compliance",
        }.get(result.domain if result else "unknown", "Unknown")
        domain_class = {
            "hr_policy": "domain-hr",
            "customer_support": "domain-support",
            "privacy_policy": "domain-privacy",
            "financial_guidelines": "domain-financial",
            "legal_compliance": "domain-legal",
        }.get(result.domain if result else "unknown", "domain-unknown")
        st.markdown(
            f'<span class="domain-badge {domain_class}">{domain_label}</span>',
            unsafe_allow_html=True,
        )
        if output_format == "excel":
            st.download_button(
                "Download CSV",
                data=formatted_answer,
                file_name="kohler_response.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
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