import streamlit as st
import requests
import PyPDF2

st.set_page_config(page_title="Legal Assistant", layout="wide")
st.title("📚 Legal Assistant")

# -------------------------
# Initialize session state
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "input_text" not in st.session_state:
    st.session_state.input_text = ""  # track input safely

uploaded_files = st.session_state.uploaded_files

# -------------------------
# Upload section
# -------------------------
st.subheader("Upload Document(s)")
uploaded = st.file_uploader(
    "Upload .txt or .pdf",
    type=["txt", "pdf"],
    accept_multiple_files=True
)

# Filter out already uploaded files
new_files = [f for f in uploaded if f not in uploaded_files] if uploaded else []

if new_files:
    uploaded_files.extend(new_files)
    backend_url = "http://127.0.0.1:8000/upload"
    files_payload = [("files", (f.name, f, f.type)) for f in new_files]

    try:
        res = requests.post(backend_url, files=files_payload)
        if res.status_code == 200:
            for f in new_files:
                st.success(f"Uploaded: {f.name}")
        else:
            st.error(f"Upload failed: {res.json().get('error', res.status_code)}")
    except Exception as e:
        st.error(f"Upload request failed: {str(e)}")

# -------------------------
# Chat section
# -------------------------
st.subheader("Ask Legal Questions")

# Display chat messages
for msg in st.session_state.messages:
    color = "#A81010" if msg["role"] == "user" else "#607CA0"
    align = "right" if msg["role"] == "user" else "left"
    st.markdown(
        f'<div style="text-align: {align}; background-color:{color}; padding:8px; border-radius:10px; margin:5px;">{msg["content"]}</div>',
        unsafe_allow_html=True,
    )

# -------------------------
# Send function
# -------------------------
def send_message():
    user_input = st.session_state.input_text
    if not user_input.strip():
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Combine uploaded files into a single context string
    context = ""
    for f in uploaded_files:
        try:
            if f.type == "application/pdf":
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        context += text + "\n"
            else:
                context += f.getvalue().decode("utf-8") + "\n"
        except Exception:
            continue
    
    backend_url = "http://127.0.0.1:8000/ask"

    with st.spinner("Assistant is thinking..."):
        try:
            params = {"query": user_input}
            res = requests.get(backend_url, params=params, timeout=60)
            if res.status_code == 200:
                answer = res.json().get("answer", "No answer returned")
            else:
                answer = f"Backend error: {res.status_code}"
        except Exception as e:
            answer = f"Request failed: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.input_text = ""  # safely clear input

# -------------------------
# Input + Send button below
# -------------------------
st.text_input("Type a message...", key="input_text")
st.button("Send", on_click=send_message)
