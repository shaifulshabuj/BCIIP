from bs4 import BeautifulSoup
import io
import re
# import pypdf # Import inside helper to avoid hard dependency if not installed yet

def normalize_text(text):
    """
    Remove extra whitespace, newlines, and non-printable characters.
    """
    if not text:
        return ""
    
    # Replace multiple newlines/spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_html(html_content):
    """
    Extract text from HTML, removing scripts, styles, etc.
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "head", "meta", "noscript"]):
        script.extract()
    
    # Get text
    text = soup.get_text(separator=' ')
    return normalize_text(text)

def extract_from_pdf(pdf_bytes):
    """
    Extract text from PDF bytes using pypdf.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        print("pypdf not installed")
        return ""
        
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return normalize_text(text)
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
