import asyncio
from pathlib import Path
import time

import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

load_dotenv()

st.set_page_config(page_title="localhost", page_icon="", layout="wide")

st.markdown(
    """
    <style>
    #MainMenu,
    [data-testid="stToolbar"],
    [data-testid="stHeaderActionElements"] {
        visibility: hidden !important;
    }
    h1, h2 {
        text-align: center;
    }
    .block-container {
        padding-bottom: 4rem;
    }
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 0.75rem;
        text-align: center;
        background: var(--background-color);
        z-index: 1000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)


def save_uploaded_file(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / Path(file.name).name
    file_path.write_bytes(file.getbuffer())
    return file_path


async def send_rag_ingest_event(file_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "file_path": str(file_path.resolve()),
                "source_id": file_path.name,
            },
        )
    )


st.title("Document Q&A Assistant")
uploaded = st.file_uploader(
    "Upload or drag and drop a Document",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True,
)

if uploaded:
    with st.spinner("Uploading and triggering ingestion..."):
        for file in uploaded:
            path = save_uploaded_file(file)
            asyncio.run(send_rag_ingest_event(path))
            time.sleep(0.3)

async def send_rag_query_event(question: str, top_k: int) -> None:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={
                "question": question,
                "top_k": top_k,
            },
        )
    )

    return result[0]


def _inngest_api_base() -> str:
    # Local dev server default; configurable via env
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
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
                raise RuntimeError(f"Function run {status}")
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for run output (last status: {last_status})")
        time.sleep(poll_interval_s)


with st.form("rag_query_form"):
    question = st.text_input("Question")
    text_to_find = st.text_input("Search")
    ask_submitted = st.form_submit_button("Ask")
    find_submitted = st.form_submit_button("Search")

    if ask_submitted and question.strip():
        query = question.strip()
        result_title = "Answer"
    elif find_submitted and text_to_find.strip():
        query = (
            f'Find the exact text "{text_to_find.strip()}" in the uploaded documents. '
            "Report matching passages and their sources."
        )
        result_title = "Text search results"
    else:
        query = None

    if query:
        with st.spinner("Searching..."):
            event_id = asyncio.run(send_rag_query_event(query, 5))
            output = wait_for_run_output(event_id)
            answer = output.get("answer", "")
            sources = output.get("sources", [])

        st.subheader(result_title)
        st.write(answer or "(No results)")
        if sources:
            st.caption("Sources")
            for source in sources:
                st.write(f"- {source}")

# st.markdown("---")
st.markdown('<div class="fixed-footer">© 2026</div>', unsafe_allow_html=True)