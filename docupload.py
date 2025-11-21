import streamlit as st
import base64
import requests
from pydantic import BaseModel

class Document(BaseModel):
    filename: str
    type: str
    file_path: str

st.title("📎 Upload Documents")
print("Document upload UI loaded")  # Debug log
if "application_id" not in st.session_state:
    st.error("No application ID found. Please go back and start again.")
else:
    st.markdown(f"### Upload documents for Application ID: **{st.session_state.application_id}**")

    uploaded_files = st.file_uploader(
        "Upload your passport, photos, or other documents here.",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        key="file_uploader"
    )

    if uploaded_files and st.button("Process Uploaded Document"):
        with st.spinner("Processing document..."):
            doclist = []
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.read()
                encoded_string = base64.b64encode(file_bytes).decode("utf-8")
                doclist.append(Document(
                    filename=uploaded_file.name,
                    type="passport",
                    file_path=encoded_string
                ))

            endpoint_url = f"http://localhost:8001/api/visa/applications/{st.session_state.application_id}/upload-documents"
            try:
                response = requests.post(endpoint_url, json=[doc.model_dump(mode="json") for doc in doclist], timeout=60)
                st.success("Document(s) processed successfully!")
                st.json(response.json())
            except requests.exceptions.RequestException as e:
                st.error(f"Network/API error occurred: {e}")