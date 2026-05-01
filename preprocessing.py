import re


def clean_text(text):
    text = re.sub(r'[Рр]ис\.?\s*\d+', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?()\-\u0400-\u04FF]', '', text)
    return text.lower().strip()


def split_into_chunks(text, max_length=2000):
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(" ".join(current)) > max_length:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks