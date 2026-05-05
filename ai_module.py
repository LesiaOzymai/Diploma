import os
import time
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
load_dotenv()


API_KEY = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]
# Отримує API ключ із змінних середовища або конфігурації Streamlit

client = Groq(api_key=API_KEY)
# Ініціалізує клієнт для роботи з Groq API

MODEL_ID = "llama-3.3-70b-versatile"
# Визначає модель, яка буде використовуватись для генерації


def clean_json_response(text: str) -> str:
    # Очищує відповідь моделі від markdown-обгорток для коректного парсингу JSON
    text = text.strip()

    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return text.strip()


def generate_summary(text, keywords):
    # Генерує структурований конспект тексту з використанням LLM та ключових слів
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

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )

    return response.choices[0].message.content
    # Повертає згенерований конспект


def generate_questions(text):
    # Генерує тестові питання у форматі JSON на основі тексту
    prompt = f"""
    Ти викладач. Згенеруй 5 тестових питань по тексту.

    ПОВЕРНИ ТІЛЬКИ JSON МАСИВ (без пояснень)

    Формат:
    [
      {{
        "question": "Текст питання?",
        "options": ["Варіант 1", "Варіант 2", "Варіант 3", "Варіант 4"],
        "correct": "Варіант 1"
      }}
    ]

    Текст:
    {text}
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )

    return clean_json_response(response.choices[0].message.content)
    # Повертає очищений JSON із питаннями


def safe_generate(func, *args):
    # Виконує виклик функції з повторними спробами у разі помилки
    for attempt in range(3):
        try:
            return func(*args)
        except Exception as e:
            print(f"[ERROR] Attempt {attempt+1}: {str(e)}")
            # Виводить інформацію про помилку та номер спроби
            time.sleep(2)
            # Робить паузу перед повторною спробою
    return None
    # Повертає None, якщо всі спроби завершились невдало