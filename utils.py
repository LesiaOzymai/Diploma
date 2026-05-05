def truncate_text(text, max_length=5000):
    # Обрізає текст до максимально дозволеної довжини для уникнення перевантаження обробки
    return text[:max_length]


def format_keywords(keywords):
    # Перетворює список ключових слів у рядок, розділений комами для зручного відображення
    return ", ".join(keywords)


def format_timestamp(ts):
    # Конвертує часову мітку у рядковий формат для подальшого використання або виводу
    return str(ts)