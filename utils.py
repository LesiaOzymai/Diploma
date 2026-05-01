def truncate_text(text, max_length=5000):
    return text[:max_length]


def format_keywords(keywords):
    return ", ".join(keywords)


def format_timestamp(ts):
    return str(ts)