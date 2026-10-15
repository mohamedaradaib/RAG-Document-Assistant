import asyncio
import hashlib
import time
from urllib.parse import quote

import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

from vector_db import QdrantStorage

load_dotenv()

st.set_page_config(page_title="RAG Document Assistant", page_icon="", layout="wide")

st.markdown(
    """
    <style>
    #MainMenu,
    [data-testid="stToolbar"],
    [data-testid="stHeaderActionElements"] {
        visibility: hidden !important;
    }
    :root {
        --gray-950: #191b1d;
        --gray-900: #202224;
        --gray-800: #292c2f;
        --gray-700: #2b2f36;
        --gray-600: #3a3f46;
        --gray-500: #6b7280;
        --gray-300: #d1d5db;
        --gray-100: #f3f4f6;
    }
    html, body, [data-testid="stAppViewContainer"], .stApp, section.main, .main {
        background: var(--gray-700) !important;
        color: var(--gray-100) !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        background: var(--gray-700) !important;
    }
    [data-testid="stHeader"] {
        background: var(--gray-950) !important;
        border-bottom: none !important;
    }
    [data-testid="stPopover"] {
        position: fixed !important;
        top: 0.625rem;
        right: 1.25rem;
        width: max-content !important;
        z-index: 1000000;
    }
    [data-testid="stPopoverButton"] {
        background: var(--gray-950) !important;
        color: var(--gray-100) !important;
        border: 1px solid rgba(209, 213, 219, 0.18) !important;
        border-radius: 10px !important;
    }
    [data-testid="stPopoverButton"]:hover {
        background: var(--gray-800) !important;
        border-color: rgba(209, 213, 219, 0.36) !important;
    }
    [data-testid="stSidebar"] {
        background: var(--gray-900) !important;
        color: var(--gray-100) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--gray-100) !important;
    }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    [data-testid="stFileUploader"] {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    [data-testid="stFileUploader"] > label,
    .stTextInput > label,
    .stTextArea > label,
    .stSlider > label,
    .stSelectbox > label,
    .stNumberInput > label,
    p, label, div, span, li, a, button, input, textarea {
        color: var(--gray-100) !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        width: min(100%, 15rem);
        aspect-ratio: 1;
        min-height: 0 !important;
        margin: 0 auto;
        padding: 1rem;
        gap: 0.75rem;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1.5px dashed rgba(209, 213, 219, 0.4);
        border-radius: 16px;
        background: var(--gray-900) !important;
        box-shadow: inset 0 0 0 1px rgba(180, 180, 180, 0.12);
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }
    [data-testid="stFileUploaderDropzone"] button,
    .stButton > button,
    [data-testid="stFormSubmitButton"] button {
        background: var(--gray-950) !important;
        color: var(--gray-100) !important;
        border: 1px solid rgba(209, 213, 219, 0.18) !important;
        border-radius: 10px !important;
        font-weight: 600;
        padding: 0.6rem 1.1rem;
    }
    [data-testid="stFileUploaderDropzone"] button:hover,
    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: var(--gray-800) !important;
        border-color: rgba(209, 213, 219, 0.36) !important;
    }
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select,
    .stNumberInput input {
        background: var(--gray-900) !important;
        color: var(--gray-100) !important;
        border: 1px solid rgba(209, 213, 219, 0.2) !important;
        border-radius: 10px;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: rgba(209, 213, 219, 0.7) !important;
    }
    [data-testid="stSlider"] [data-rac][data-orientation="horizontal"] > div[data-rac] > div:first-child {
        background: var(--gray-100) !important;
    }
    [data-testid="stSlider"] [data-rac][data-orientation="horizontal"] > div[data-rac] > div[data-rac] {
        background: var(--gray-100) !important;
        border: 2px solid var(--gray-900) !important;
    }
    [data-testid="stSlider"] [data-rac][data-orientation="horizontal"] > div[data-rac] > div[data-rac]:active,
    [data-testid="stSlider"] [data-rac][data-orientation="horizontal"] > div[data-rac] > div[data-rac]:focus-within {
        background: var(--gray-600) !important;
        box-shadow: 0 0 0 3px rgba(58, 63, 70, 0.55) !important;
    }
    h1, h2 {
        text-align: center;
    }
    h1 {
        font-size: 1.5rem;
        line-height: 1.2;
        letter-spacing: 0;
        font-weight: 700;
        margin: 0 0 1rem 0;
        color: var(--gray-100);
    }
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        box-sizing: border-box;
        padding: 0.75rem;
        text-align: center;
        font-size: 0.8rem;
        color: var(--gray-300);
        background: var(--gray-950);
        border-top: 1px solid rgba(209, 213, 219, 0.12);
        z-index: 1000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    is_production = os.getenv("INNGEST_IS_PRODUCTION", "false").lower() == "true"
    return inngest.Inngest(app_id="rag_app", is_production=is_production)


def upload_document(file) -> str:
    api_base = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    headers = {"X-File-Name": quote(file.name, safe="")}
    api_token = os.getenv("APP_API_TOKEN")
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"

    response = requests.post(
        f"{api_base}/upload",
        data=file.getvalue(),
        headers=headers,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["event_id"]


header_slot = st.empty()
uploaded = st.file_uploader(
    "Upload or drag and drop a Document",
    type=["pdf", "docx", "html", "htm", "txt", "md"],
    accept_multiple_files=True,
)

async def send_rag_query_event(question: str, top_k: int, chat_history: list[dict] | None = None) -> None:
    client = get_inngest_client()
    payload = {
        "question": question,
        "top_k": top_k,
    }
    if chat_history:
        payload["chat_history"] = chat_history

    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data=payload,
        )
    )

    return result[0]


def _inngest_api_base() -> str:
    is_production = os.getenv("INNGEST_IS_PRODUCTION", "false").lower() == "true"
    default = "https://api.inngest.com/v1" if is_production else "http://127.0.0.1:8288/v1"
    return os.getenv("INNGEST_API_BASE", default).rstrip("/")


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    api_key = os.getenv("INNGEST_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def wait_for_run_output(event_id: str, timeout_s: float = 120.0, poll_interval_s: float = 0.5) -> dict:
    start = time.time()
    last_status = None
    while True:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            status = run.get("status")
            last_status = status or last_status
            if status in ("Completed", "Succeeded", "Success", "Finished"):
                return run.get("output") or {}
            if status in ("Failed", "Cancelled"):
                failure_reason = run.get("error") or run.get("output") or "Function run failed"
                raise RuntimeError(str(failure_reason))
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for run output (last status: {last_status})")
        time.sleep(poll_interval_s)


if "processed_uploads" not in st.session_state:
    st.session_state.processed_uploads = set()

if not uploaded:
    st.session_state.processed_uploads.clear()
else:
    for file in uploaded:
        fingerprint = (file.name, hashlib.sha256(file.getvalue()).hexdigest())
        if fingerprint in st.session_state.processed_uploads:
            continue

        with st.spinner(f"Processing {file.name}..."):
            event_id = upload_document(file)
            output = wait_for_run_output(event_id)
        st.session_state.processed_uploads.add(fingerprint)
        st.success(f"Processed {file.name}: {output.get('ingested', 0)} chunks.")

with header_slot.container():
    _, title_column, documents_column = st.columns([1, 2, 1])
    with title_column:
        st.title("RAG Document Assistant")
    with documents_column:
        with st.popover("Documents", use_container_width=True):
            try:
                indexed_sources = sorted(QdrantStorage().list_sources())
            except Exception:
                indexed_sources = []

            if indexed_sources:
                for source in indexed_sources:
                    source_column, delete_column = st.columns([4, 1])
                    source_column.write(source)
                    if delete_column.button("Delete", key=f"delete_{source}", help=f"Remove {source} from the vector index"):
                        try:
                            QdrantStorage().delete_source(source)
                            st.success(f"Removed {source}")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Couldn't remove {source}: {exc}")
            else:
                st.caption("No documents indexed yet.")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

with st.form("rag_query_form"):
    question = st.text_input("Question")
    text_to_find = st.text_input("Search")
    top_k = st.slider("Retrieval depth", min_value=1, max_value=10, value=5, step=1)
    col_ask, col_find = st.columns([1, 1])
    with col_ask:
        ask_submitted = st.form_submit_button("Ask", use_container_width=True)
    with col_find:
        find_submitted = st.form_submit_button("Search", use_container_width=True)

if ask_submitted and question.strip():
    prompt = question.strip()
    query = prompt
elif find_submitted and text_to_find.strip():
    prompt = text_to_find.strip()
    query = (
        f'Find the exact text "{prompt}" in the uploaded documents. '
        "Report matching passages and their sources."
    )
else:
    prompt = None
    query = None

if query:
    st.session_state.messages.append({"role": "user", "content": prompt})
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages[:-1]
        if msg["role"] in {"user", "assistant"}
    ]

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Searching..."):
        try:
            event_id = asyncio.run(send_rag_query_event(query, top_k, conversation_history))
            output = wait_for_run_output(event_id)
        except Exception as exc:
            output = {"answer": f"The AI service is currently unavailable: {exc}", "sources": []}

        answer = output.get("answer", "")
        sources = output.get("sources", [])

    assistant_message = {"role": "assistant", "content": answer or "I couldn't find relevant information in the uploaded documents.", "sources": sources}
    st.session_state.messages.append(assistant_message)

    with st.chat_message("assistant"):
        st.markdown(assistant_message["content"])
        if assistant_message["sources"]:
            with st.expander("Sources"):
                for source in assistant_message["sources"]:
                    st.write(f"- {source}")

st.markdown('<div class="fixed-footer">© 2026 RAG Document Assistant | About | Terms of Service | Privacy Policy | Security | Disclosure</div>', unsafe_allow_html=True)