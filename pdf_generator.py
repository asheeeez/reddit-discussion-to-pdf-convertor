from fpdf import FPDF
import os
import re
import textwrap
import unicodedata

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def break_long_words(text, max_word_length=80):
    """Break long unbroken text into chunks to avoid layout crashes."""
    words = text.split()
    safe_words = []
    for word in words:
        if len(word) > max_word_length:
            broken = [word[i:i + max_word_length] for i in range(0, len(word), max_word_length)]
            safe_words.extend(broken)
        else:
            safe_words.append(word)
    return ' '.join(safe_words)

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self._load_font()
        self.set_font("DejaVu", "", 14)
        self.add_page()

    def _load_font(self):
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
        if not os.path.isfile(font_path):
            raise FileNotFoundError(f"Font not found at {font_path}")
        self.add_font("DejaVu", "", font_path, uni=True)

    def header(self):
        self.set_font("DejaVu", "", 12)
        self.cell(0, 10, "Reddit Discussion Summary", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def clean_text(self, text):
        if not text:
            return "[empty]"

        # Remove unsupported unicode (emoji, Cntrl, Symbol)
        text = ''.join(
            c for c in text
            if unicodedata.category(c)[0] not in ('C', 'S') and 32 <= ord(c) <= 126
        )

        # Replace URLs with [link]
        text = re.sub(r'https?://\S+', '[link]', text)

        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip() or "[unrenderable comment]"

    def add_post_content(self, post_data):
        self.set_font("DejaVu", "", 14)
        title = self.clean_text(post_data.get("title", "Untitled"))
        self.multi_cell(0, 10, f"Title: {title}")

        self.set_font("DejaVu", "", 12)
        body = self.clean_text(post_data.get("body", ""))
        if body:
            self.ln(3)
            self.multi_cell(0, 10, f"Post:\n{body}")
        self.ln(10)

    def add_comments(self, comments, indent=0):
        self.set_font("DejaVu", "", 10)
        self.cell(0, 10, "Top Comments:", ln=True)

        for comment in comments:
            try:
                raw = comment.get("body", "")
                clean = self.clean_text(raw)
                broken = break_long_words(clean, max_word_length=80)
                wrapped = textwrap.wrap(broken, width=90)

                if not wrapped:
                    continue

                indent_str = " " * indent
                effective_width = 190 - indent  # avoid letting FPDF auto-calc width

                for line in wrapped:
                    self.multi_cell(effective_width, 10, indent_str + "- " + line)

                self.ln(2)

                # Recursively add replies
                if comment.get("replies"):
                    self.add_comments(comment["replies"], indent + 4)

            except Exception as e:
                print(f"[!] Error adding comment: {e}")
                continue


def generate_pdf(post_data):
    pdf = PDF()
    pdf.add_post_content(post_data)
    pdf.add_comments(post_data.get("comments", []))

    title = post_data.get("title", "reddit_post")
    filename = f"{sanitize_filename(title)}.pdf"
    pdf.output(filename)
    print(f"✅ PDF saved as: {filename}")
