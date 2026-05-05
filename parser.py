import pdfplumber


def extract_text_from_pdf(file):
    # Витягує текст із PDF-файлу посторінково з перевіркою на порожній або пошкоджений файл
    text = ""

    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    # Додає текст сторінки до загального результату
                    text += page_text + "\n"

        if not text.strip():
            # Перевіряє чи PDF не порожній після обробки
            raise ValueError("Empty PDF")

        return text

    except Exception:
        # Обробляє помилки відкриття або читання PDF
        raise ValueError("Invalid or corrupted PDF file")


def extract_text_from_txt(file):
    # Зчитує текст із TXT-файлу та декодує його у формат UTF-8
    try:
        return file.read().decode("utf-8")
    except Exception:
        # Обробляє помилки читання або неправильного кодування
        raise ValueError("Cannot read TXT file")


def extract_text(file):
    # Визначає тип файлу та викликає відповідну функцію для витягування тексту
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".txt"):
        return extract_text_from_txt(file)
    else:
        # Обробляє випадок непідтримуваного формату файлу
        raise ValueError("Unsupported file format")