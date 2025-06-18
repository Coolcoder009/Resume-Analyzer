import easyocr
import cv2


def extract_text_from_image(image_path):
    # Initialize the reader (supports multiple languages)
    reader = easyocr.Reader(['en'], gpu=True)

    # Read and extract text
    result = reader.readtext(image_path, detail=0)

    # Join extracted lines into one string
    extracted_text = '\n'.join(result)

    return extracted_text

# Example usage
image_path = r"C:\Users\dgcon\Downloads\Resume.jpg"
text = extract_text_from_image(image_path)
print("Extracted Text:\n", text)
