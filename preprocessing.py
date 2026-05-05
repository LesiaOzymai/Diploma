import re


def clean_text(text):
    # Очищує текст від службових позначень, зайвих символів і приводить його до нижнього регістру
    text = re.sub(r'[Рр]ис\.?\s*\d+', '', text)
    # Видаляє згадки типу "Рис. 1", "рис 2" тощо
    text = re.sub(r'\n+', '\n', text)
    # Замінює кілька переносів рядка на один
    text = re.sub(r'\s+', ' ', text)
    # Прибирає зайві пробіли
    text = re.sub(r'[^\w\s.,!?()\-\u0400-\u04FF]', '', text)
    # Видаляє всі символи, окрім букв, цифр і базової пунктуації
    return text.lower().strip()


def split_into_chunks(text, max_length=2000):
    # Розбиває текст на частини обмеженої довжини для подальшої обробки
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        # Додає слова до поточного блоку
        if len(" ".join(current)) > max_length:
            chunks.append(" ".join(current))
            current = []

    if current:
        # Додає залишок тексту як окремий блок
        chunks.append(" ".join(current))

    return chunks