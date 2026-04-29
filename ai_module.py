import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

MODEL_ID = "llama-3.3-70b-versatile"


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
    - Ігноруй артефакти PDF
    - Відповідай українською
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_ID,
    )

    return response.choices[0].message.content


def generate_questions(text):
    prompt = f"""
    Ти викладач.

    Текст:
    {text}

    Створи 5 тестових питань:
    - 4 варіанти (A, B, C, D)
    - тільки 1 правильний
    - в кінці правильна відповідь
    - українською мовою
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_ID,
    )

    return response.choices[0].message.content


def safe_generate(func, *args):
    for attempt in range(3):
        try:
            return func(*args)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    return "Не вдалося отримати відповідь від ШІ."