import re

def clean_text(text):
    text = re.sub(r'[Рр]ис\.?\s*\d+', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?()\-\u0400-\u04FF]', '', text)
    text = text.lower()

    return text.strip()


def split_into_chunks(text, max_length=1000):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)

        if len(" ".join(current_chunk)) > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks