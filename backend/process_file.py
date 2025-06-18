from pypdf import PdfReader
from docx import Document
import easyocr
import cv2
import numpy as np
import io

def extract_pdf(resume):
    reader = PdfReader(resume)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text.strip()

def extract_docs(file_obj):
    file_bytes = file_obj.read()  # Read bytes from SpooledTemporaryFile
    doc = Document(io.BytesIO(file_bytes))  # Wrap in a BytesIO stream
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)

def extract_image(uploaded_file):
    file_bytes = uploaded_file.read()
    np_arr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    reader = easyocr.Reader(['en'], gpu=True)
    result = reader.readtext(image, detail=0)
    return '\n'.join(result)


