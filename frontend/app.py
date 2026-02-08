import streamlit as st
import requests

# API URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Ultra Doc-Intelligence", layout="wide")
st.title(" Ultra Doc-Intelligence: TMS Assistant")

# Sidebar for Upload
with st.sidebar:
    st.header("1. Upload Document")
    uploaded_file = st.file_uploader("Upload Rate Con, BOL, or Invoice", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            with st.spinner("Processing..."):
                response = requests.post(f"{API_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success("Document uploaded & indexed!")
                else:
                    st.error("Upload failed.")

# Main Area
col1, col2 = st.columns(2)

with col1:
    st.header("2. Ask Questions")
    question = st.text_input("Ask about the shipment (e.g., 'What is the rate?')")
    
    if st.button("Ask AI"):
        if question:
            with st.spinner("Thinking..."):
                payload = {"question": question}
                res = requests.post(f"{API_URL}/ask", json=payload).json()
                
                # Confidence Meter
                score = res.get("confidence", 0)
                st.metric("Confidence Score", f"{score * 100:.1f}%")
                
                if score < 0.6:
                    st.warning("⚠️ Low confidence. Verify with source.")
                else:
                    st.success("✅ High confidence.")
                
                st.markdown(f"**Answer:** {res['answer']}")
                
                with st.expander("View Source Context"):
                    st.write(res.get("sources"))

with col2:
    st.header("3. Structured Extraction")
    st.write("Extract standardized JSON data.")
    
    if st.button("Run Extraction"):
        with st.spinner("Extracting..."):
            res = requests.post(f"{API_URL}/extract").json()
            st.json(res)