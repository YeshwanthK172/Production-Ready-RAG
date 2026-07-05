from pathlib import Path
import time
import streamlit as st
from dotenv import load_dotenv
import os
import requests

load_dotenv()

st.set_page_config(page_title="RAG Ingest PDF", page_icon="📄", layout="centered")

# --- Helper to Send Events via Standard REST API ---
def send_inngest_event_sync(event_name: str, data: dict) -> str:
    """Sends an event to Inngest using standard synchronous HTTP requests."""
    event_key = os.getenv("INNGEST_EVENT_KEY")
    if not event_key:
        st.error("❌ INNGEST_EVENT_KEY is missing from environment secrets.")
        st.stop()
        
    url = "https://api.inngest.com/v1/events"
    headers = {
        "Authorization": f"Bearer {event_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": event_name,
        "data": data
    }
    
    # Send a standard POST request
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    
    # Inngest returns an object containing an array of sent event IDs
    res_data = resp.json()
    if "ids" in res_data and len(res_data["ids"]) > 0:
        return res_data["ids"][0]
    return ""

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path

# --- UI Setup ---
st.title("Upload a PDF to Ingest")
uploaded = st.file_uploader("Choose a PDF", type=["pdf"], accept_multiple_files=False)

if uploaded is not None:
    with st.spinner("Uploading and triggering ingestion..."):
        path = save_uploaded_pdf(uploaded)
        
        # Fire event synchronously using our new REST helper
        send_inngest_event_sync(
            event_name="rag/ingest_pdf",
            data={
                "pdf_path": str(path.resolve()),
                "source_id": path.name,
            }
        )
        time.sleep(0.3)
    st.success(f"Triggered ingestion for: {path.name}")
    st.caption("You can upload another PDF if you like.")

st.divider()
st.title("Ask a question about your PDFs")

def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "https://api.inngest.com/v1")

def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    
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
            # Fire event synchronously using our new REST helper
            event_id = send_inngest_event_sync(
                event_name="rag/query_pdf_ai",
                data={
                    "question": question.strip(),
                    "top_k": int(top_k),
                }
            )
            
            # Poll for results
            output = wait_for_run_output(event_id)
            answer = output.get("answer", "")
            sources = output.get("sources", [])

        st.subheader("Answer")
        st.write(answer or "(No answer)")
        if sources:
            st.caption("Sources")
            for s in sources:
                st.write(f"- {s}")
