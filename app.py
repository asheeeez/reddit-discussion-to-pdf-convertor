import streamlit as st
import tempfile
import os
from reddit_scraper import fetch_post_data
from pdf_generator import generate_pdf

st.set_page_config(page_title="Reddit to PDF", layout="centered")

st.title("📄 Reddit to PDF Converter")
st.markdown("Paste a Reddit post URL and download a clean PDF of the discussion.")

url = st.text_input("🔗 Reddit Post URL")

if st.button("📦 Generate PDF") and url:
    with st.spinner("Fetching and generating PDF..."):
        try:
            post_data = fetch_post_data(url)

            # Use a temporary file for the PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                pdf_path = tmp_file.name
                post_data['title'] = post_data.get('title', 'reddit_post')  # fallback title
                generate_pdf(post_data, filename=pdf_path)

            with open(pdf_path, "rb") as f:
                st.success("✅ PDF generated!")
                st.download_button(
                    label="📥 Download PDF",
                    data=f,
                    file_name=f"{post_data['title']}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"❌ Failed: {str(e)}")
