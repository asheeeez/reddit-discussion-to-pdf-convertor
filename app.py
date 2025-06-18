import streamlit as st
import tempfile
import os
from reddit_scraper import fetch_post_data
from pdf_generator import generate_pdf

st.set_page_config(page_title="Reddit to PDF", layout="centered")

# Initialize state
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = ""

st.title("📄 Reddit to PDF Converter")
st.markdown("Paste a Reddit post URL and download a clean PDF of the discussion.")

url = st.text_input("🔗 Reddit Post URL")

if st.button("📦 Generate PDF") and url:
    with st.spinner("Fetching and generating PDF..."):
        try:
            post_data = fetch_post_data(url)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                pdf_path = tmp_file.name
                post_data['title'] = post_data.get('title', 'reddit_post')
                generate_pdf(post_data, filename=pdf_path)

                # Set session state
                st.session_state.pdf_ready = True
                st.session_state.pdf_path = pdf_path
                st.session_state.pdf_name = f"{post_data['title']}.pdf"

        except Exception as e:
            st.error(f"❌ Failed: {str(e)}")

# Show download button only after PDF is ready
if st.session_state.pdf_ready:
    with open(st.session_state.pdf_path, "rb") as f:
        st.success("✅ PDF generated!")
        if st.download_button(
            label="📥 Download PDF",
            data=f,
            file_name=st.session_state.pdf_name,
            mime="application/pdf",
            key="download_button"
        ):
            # Clear and refresh after successful download
            st.session_state.pdf_ready = False
            st.rerun()
