import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

MODEL_ID = "llama-3.3-70b-versatile"


def clean_json_response(text):
    text = text.strip()

    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return text.strip()


def generate_summary(text, keywords):
    prompt = f"""
    Ти — експерт з аналізу навчальних матеріалів.

    Текст:
    {text}

    Ключові слова:
    {", ".join(keywords)}

    Завдання:
    - Створи структурований конспект (5-7 пунктів)
    - Пояснюй просто
    - Відповідай українською
    """
    # noinspection PyTypeChecker
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_ID,
    )

    return response.choices[0].message.content


def generate_questions(text):
    prompt = f"""
    Ти викладач.

    Згенеруй 5 тестових питань по тексту.

    ПОВЕРНИ ТІЛЬКИ JSON МАСИВ (без пояснень)

    Формат:
    [
      {{
        "question": "Питання?",
        "options": ["A", "B", "C", "D"],
        "correct": "A"
      }}
    ]

    Текст:
    {text}
    """
    # noinspection PyTypeChecker
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_ID,
    )

    return clean_json_response(response.choices[0].message.content)


def safe_generate(func, *args):
    for _ in range(3):
        try:
            return func(*args)
        except Exception:
            time.sleep(2)

    return None