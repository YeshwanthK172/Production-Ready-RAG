import asyncio
from pathlib import Path
import time
import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

load_dotenv()

st.set_page_config(page_title="RAG Ingest PDF", page_icon="📄", layout="centered")

# --- Dynamic Client Configuration ---
@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    # If an Inngest Event Key exists in env, switch automatically to production mode
    is_prod = os.getenv("INNGEST_EVENT_KEY") is not None
    return inngest.Inngest(
        app_id="rag_app", 
        is_production=is_prod,
        event_key=os.getenv("INNGEST_EVENT_KEY")
    )

# --- Safe Async Helper for Streamlit Loop ---
def run_async(coro):
    """Safely runs async functions inside Streamlit's threaded environment."""
    try:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path

async def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )

st.title("Upload a PDF to Ingest")
uploaded = st.file_uploader("Choose a PDF", type=["pdf"], accept_multiple_files=False)

if uploaded is not None:
    with st.spinner("Uploading and triggering ingestion..."):
        path = save_uploaded_pdf(uploaded)
        # Use our safe runner helper
        run_async(send_rag_ingest_event(path))
        time.sleep(0.3)
    st.success(f"Triggered ingestion for: {path.name}")
    st.caption("You can upload another PDF if you like.")

st.divider()
st.title("Ask a question about your PDFs")

async def send_rag_query_event(question: str, top_k: int) -> str:
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
    # Dynamically point to cloud REST endpoint if local fallback is absent
    return os.getenv("INNGEST_API_BASE", "https://api.inngest.com/v1")

def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    
    # Authenticate cloud polling using Cloud Signing Key or Event Key if present
    headers = {}
    signing_key = os.getenv("INNGEST_SIGNING_KEY") or os.getenv("INNGEST_EVENT_KEY")
    if signing_key:
        headers["Authorization"] = f"Bearer {signing_key}"
        
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])

def wait_for_run_output(event_id: str, timeout_s: float = 120.0, poll_interval_s: float = 1.0) -> dict:
    start = time.time()
    last_status = None
    while True:
        try:
            runs = fetch_runs(event_id)
            if runs:
                run = runs[0]
                status = run.get("status")
                last_status = status or last_status
                if status in ("Completed", "Succeeded", "Success", "Finished"):
                    return run.get("output") or {}
                if status in ("Failed", "Cancelled"):
                    raise RuntimeError(f"Function run status: {status}")
        except Exception as e:
            # Prevent minor poll blips from breaking the execution chain completely
            st.caption(f"Polling update trace: {e}")
            
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for run output (last status: {last_status})")
        time.sleep(poll_interval_s)

with st.form("rag_query_form"):
    question = st.text_input("Your question")
    top_k = st.number_input("How many chunks to retrieve", min_value=1, max_value=20, value=5, step=1)
    submitted = st.form_submit_button("Ask")

    if submitted and question.strip():
        with st.spinner("Sending event and generating answer..."):
            # Execute safely with the async loop wrapper
            event_id = run_async(send_rag_query_event(question.strip(), int(top_k)))
            output = wait_for_run_output(event_id)
            answer = output.get("answer", "")
            sources = output.get("sources", [])

        st.subheader("Answer")
        st.write(answer or "(No answer)")
        if sources:
            st.caption("Sources")
            for s in sources:
                st.write(f"- {s}")
