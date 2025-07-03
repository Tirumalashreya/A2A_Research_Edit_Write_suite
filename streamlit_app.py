import streamlit as st
import requests
import io

def read_file_as_text(uploaded_file):
    if uploaded_file is not None:
        content = uploaded_file.read()
        try:
            return content.decode("utf-8")
        except Exception:
            return content.decode(errors="ignore")
    return ""

st.set_page_config(page_title="AI Research Companion", layout="centered")
st.title("AI Research Companion")
st.markdown("Draft, Edit, and Generate PDFs using Agent-to-Agent Protocol")
st.markdown("---")

workflow = st.radio(
    "Choose your workflow:",
    [
        "Research Only",
        "Edit Only",
        "Write (with Research)",
        "Full Workflow (Research → Write → Edit → Export)",
        "Structure/Clean Uploaded Research"
    ],
    index=0
)

if workflow == "Research Only":
    st.header("Research Only")
    topic = st.text_input("Enter your research topic:")
    if st.button("Start Research", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Researching..."):
                try:
                    resp = requests.post("http://localhost:8000/research", json={"topic": topic.strip()})
                    if resp.ok:
                        result = resp.json().get("result", "No result returned.")
                        st.success("Research Result:")
                        st.markdown(f"<div style='background:#222;padding:1em;border-radius:8px;color:#fff'>{result}</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

elif workflow == "Edit Only":
    st.header("Edit Only")
    st.write("Paste your content or upload a file to edit.")
    content = st.text_area("Paste content here:", height=150)
    uploaded = st.file_uploader("Or upload a file (txt, docx, pdf):", type=["txt", "docx", "pdf"])
    edit_content = content.strip() or read_file_as_text(uploaded)
    if st.button("Edit Content", use_container_width=True):
        if not edit_content:
            st.warning("Please paste or upload content to edit.")
        else:
            with st.spinner("Editing content..."):
                try:
                    resp = requests.post("http://localhost:8000/edit", json={"content": edit_content})
                    if resp.ok:
                        result = resp.json().get("result", "No result returned.")
                        st.success("Edited Content:")
                        st.markdown(f"<div style='background:#222;padding:1em;border-radius:8px;color:#fff'>{result}</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

elif workflow == "Write (with Research)":
    st.header("Write (with Research)")
    topic = st.text_input("Enter your article topic:")
    st.write("(Optional) Paste or upload research content to guide the writing.")
    research = st.text_area("Paste research here:", height=100)
    uploaded = st.file_uploader("Or upload research file (txt, docx, pdf):", type=["txt", "docx", "pdf"])
    research_content = research.strip() or read_file_as_text(uploaded)
    if st.button("Draft Article", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Drafting article..."):
                try:
                    payload = {"topic": topic.strip()}
                    if research_content:
                        payload["research"] = research_content
                    resp = requests.post("http://localhost:8000/write", json=payload)
                    if resp.ok:
                        result = resp.json().get("result", "No result returned.")
                        st.success("Drafted Article:")
                        st.markdown(f"<div style='background:#222;padding:1em;border-radius:8px;color:#fff'>{result}</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

elif workflow == "Full Workflow (Research → Write → Edit → Export)":
    st.header("Full Workflow: Research → Write → Edit → Export")
    topic = st.text_input("Enter your topic for the full workflow:")
    if st.button("Run Full Workflow", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Running full workflow..."):
                try:
                    resp = requests.post("http://localhost:8000/full_workflow", json={"topic": topic.strip()})
                    if resp.ok:
                        data = resp.json()
                        result = data.get("result", "No result returned.")
                        st.success("Final Content:")
                        st.markdown(f"<div style='background:#222;padding:1em;border-radius:8px;color:#fff'>{result}</div>", unsafe_allow_html=True)
                        # Show download links if available
                        pdf_url = data.get("pdf_url")
                        docx_url = data.get("docx_url")
                        if pdf_url or docx_url:
                            st.markdown("---")
                            st.subheader("Download Files:")
                            if pdf_url:
                                st.markdown(f"[Download PDF]({pdf_url})", unsafe_allow_html=True)
                            if docx_url:
                                st.markdown(f"[Download Word]({docx_url})", unsafe_allow_html=True)
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

elif workflow == "Structure/Clean Uploaded Research":
    st.header("Structure or Clean Uploaded Research")
    st.write("Upload a research file or paste your research content below. The system will organize and clean it for you.")
    uploaded = st.file_uploader("Upload research file (txt, docx, pdf)", type=["txt", "docx", "pdf"])
    pasted = st.text_area("Or paste your research content here:", height=200)
    research_content = ""
    if uploaded:
        research_content = read_file_as_text(uploaded)
    elif pasted.strip():
        research_content = pasted.strip()
    submit_col, _ = st.columns([1, 3])
    with submit_col:
        if st.button("Structure Research", use_container_width=True):
            if not research_content:
                st.warning("Please upload or paste research content.")
            else:
                with st.spinner("Structuring research..."):
                    try:
                        resp = requests.post(
                            "http://localhost:8000/structure_research",
                            json={"research": research_content}
                        )
                        if resp.ok:
                            result = resp.json().get("result", "No result returned.")
                            st.success("Structured Research Output:")
                            st.markdown(f"<div style='background:#222;padding:1em;border-radius:8px;color:#fff'>{result}</div>", unsafe_allow_html=True)
                        else:
                            st.error(f"Error: {resp.text}")
                    except Exception as e:
                        st.error(f"Request failed: {e}")

# Remove the following lines at the end:
# if __name__ == "__main__":
#     main() 