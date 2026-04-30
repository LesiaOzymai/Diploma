import pdfplumber


def extract_text_from_pdf(file):
    text = ""

    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            raise ValueError("Empty PDF")

        return text

    except Exception:
        raise ValueError("Invalid or corrupted PDF file")


def extract_text_from_txt(file):
    try:
        return file.read().decode("utf-8")
    except Exception:
        raise ValueError("Cannot read TXT file")


def extract_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".txt"):
        return extract_text_from_txt(file)
    else:
        raise ValueError("Unsupported file format")