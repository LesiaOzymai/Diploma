import re


import re

def clean_text(text):
    # прибираємо "Рис.13", "рис. 15"
    text = re.sub(r'[Рр]ис\.?\s*\d+', '', text)

    # прибираємо зайві переноси
    text = re.sub(r'\n+', '\n', text)

    # прибираємо зайві пробіли
    text = re.sub(r'\s+', ' ', text)

    # залишаємо тільки потрібні символи (з підтримкою укр)
    text = re.sub(r'[^\w\s.,!?()\-\u0400-\u04FF]', '', text)

    # нижній регістр
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