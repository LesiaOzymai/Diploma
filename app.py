import streamlit as st
import json
import random

from parser import extract_text
from preprocessing import clean_text, split_into_chunks
from keywords import extract_keywords
from summarizer import summarize_text
from ai_module import generate_summary, generate_questions, safe_generate
from db import init_db, save_analysis, get_history, delete_analysis, clear_history

# КОНФІГУРАЦІЯ
st.set_page_config(page_title="AI Text Analyzer", layout="wide", initial_sidebar_state="expanded")
# Налаштовує параметри сторінки Streamlit

# СТИЛІ
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Картки та мікроанімації */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* УСІ КНОПКИ  */
.stButton > button, div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #6e8efb, #a777e3) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    height: 45px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 4px 12px rgba(167, 119, 227, 0.4) !important;
}

/* ФІОЛЕТОВІ РАДІОКНОПКИ В ТЕСТАХ (Жорстке перекриття стандартного червоного) */
div[data-baseweb="radio"] > div {
    border-radius: 50%;
    border: 2px solid #a777e3 !important;
}

/* Вибрана кнопка */
div[data-baseweb="radio"] input:checked ~ div {
    border-color: #a777e3 !important;
}

/* Внутрішня точка */
div[data-baseweb="radio"] input:checked ~ div > div {
    background-color: #a777e3 !important;
}

/* Hover ефект */
div[data-baseweb="radio"]:hover > div {
    border-color: #8b5cf6 !important;
}

/* Стилізація бокового меню */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(167, 119, 227, 0.2);
}

/* Збільшуємо текст навігації */
section[data-testid="stSidebar"] .stRadio p {
    font-size: 18px !important;
    font-weight: 500;
    display: flex;
    align-items: center;
}

/* Додаємо кастомні фіолетові SVG іконки до пунктів меню */
section[data-testid="stSidebar"] .stRadio label:nth-child(1) p::before {
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23a777e3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>');
    margin-right: 12px;
    margin-top: 4px;
}
section[data-testid="stSidebar"] .stRadio label:nth-child(2) p::before {
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23a777e3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>');
    margin-right: 12px;
    margin-top: 4px;
}
section[data-testid="stSidebar"] .stRadio label:nth-child(3) p::before {
    content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23a777e3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>');
    margin-right: 12px;
    margin-top: 4px;
}

/* ПРИХОВУВАННЯ СТАНДАРТНИХ КРУЖЕЧКІВ У БІЧНОМУ МЕНЮ */
section[data-testid="stSidebar"] .stRadio label > div:first-of-type {
    display: none !important;
}

/* Стилізуємо фони пунктів меню при виборі */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 8px 12px;
    border-radius: 8px;
    transition: background-color 0.2s ease;
    margin-bottom: 4px;
    cursor: pointer;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: rgba(167, 119, 227, 0.05);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background-color: rgba(167, 119, 227, 0.15) !important;
}
</style>
""", unsafe_allow_html=True)
# Додає кастомні CSS стилі для покращення інтерфейсу

init_db()
# Ініціалізує базу даних при запуску застосунку

# СТАН СЕСІЇ
if "selected_analysis" not in st.session_state:
    st.session_state.selected_analysis = None
if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = ""
if "questions" not in st.session_state:
    st.session_state.questions = ""
if "score" not in st.session_state:
    st.session_state.score = None
if "confirm_delete_all" not in st.session_state:
    st.session_state.confirm_delete_all = False
# Ініціалізує змінні стану для збереження даних між перерендерингами

# БІЧНА ПАНЕЛЬ
with st.sidebar:
    st.markdown("### Навігація")
    mode = st.radio("Оберіть розділ:", ["Аналіз тексту", "Навчання", "Історія аналізів"], label_visibility="collapsed")
    st.divider()
    st.markdown("""
    <div style='margin-top: 20px; text-align: left;'>
        <p style='color: #9CA3AF; font-size: 14px; margin-bottom: 2px;'>AI Educational System v1.0</p>
        <p style='color: #a777e3; font-size: 14px; font-weight: 600; margin-top: 0;'>by Lesia Ozymai</p>
    </div>
    """, unsafe_allow_html=True)
# Створює бічне меню для перемикання режимів

# ЗАГОЛОВОК
st.markdown("""
<div style="padding: 10px 0 20px 0;">
    <h1 style="font-size:42px; margin-bottom:5px; background: -webkit-linear-gradient(45deg, #6e8efb, #a777e3); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI Text Analyzer</h1>
    <p style="font-size:18px; color:#9CA3AF;">
        Інтелектуальний аналіз навчальних матеріалів із використанням NLP та LLM
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()
# Відображає заголовок та опис застосунку


# РЕЖИМ АНАЛІЗУ

if mode == "Аналіз тексту":
    # Основний режим для завантаження та аналізу тексту

    with st.container(border=True):
        st.subheader("Завантаження файлу")
        file = st.file_uploader("Оберіть PDF або TXT файл (5-7 сторінок)", type=["pdf", "txt"])

        if file is not None:
            st.caption(f"Файл: {file.name} • Розмір: {round(file.size / 1024, 2)} KB")
            # Відображає інформацію про завантажений файл

    if file is not None:
        try:
            raw_text = extract_text(file)
            # Витягує текст із файлу
        except Exception:
            st.error("Файл пошкоджений або не читається. Спробуйте інший.")
            st.stop()

        clean = clean_text(raw_text)
        # Очищує текст від зайвих символів

        keywords = extract_keywords(clean)
        # Витягує ключові слова

        summary = summarize_text(clean)
        # Генерує класичний конспект

        chunks = split_into_chunks(raw_text, max_length=15000)
        # Розбиває текст на частини для AI обробки

        text_for_ai = chunks[0] if chunks else raw_text
        # Обирає перший chunk для генерації

        tab1, tab2 = st.tabs(["Класичний NLP", "AI Аналіз (Groq)"])
        # Створює вкладки для різних типів аналізу

        with tab1:
            with st.container(border=True):
                st.markdown("#### Ключові слова")
                st.info(", ".join(keywords))
                # Відображає ключові слова

            with st.container(border=True):
                st.markdown("#### Класичний конспект")
                st.text_area("Екстрактивна сумаризація", summary, height=250)
                # Показує результат класичної сумаризації

        with tab2:
            with st.container(border=True):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Згенерувати AI конспект", use_container_width=True,
                                 disabled=bool(st.session_state.ai_summary)):
                        with st.spinner("ШІ аналізує текст..."):
                            st.session_state.ai_summary = safe_generate(generate_summary, text_for_ai, keywords)
                            # Генерує AI конспект із обробкою помилок

                with col2:
                    if st.button("Згенерувати тест", use_container_width=True,
                                 disabled=bool(st.session_state.questions)):
                        with st.spinner("ШІ створює питання..."):
                            st.session_state.questions = safe_generate(generate_questions, text_for_ai)
                            # Генерує тестові питання

            res_col1, res_col2 = st.columns(2)

            with res_col1:
                if st.session_state.ai_summary:
                    with st.container(border=True):
                        st.markdown("#### AI Конспект")
                        st.write(st.session_state.ai_summary)
                        # Відображає AI конспект

            with res_col2:
                if st.session_state.questions:
                    with st.container(border=True):
                        st.markdown("#### Питання")
                        st.success("Тест готовий! Перейдіть у вкладку 'Навчання' в бічному меню.")
                        # Повідомляє про готовність тесту

            if st.session_state.ai_summary or st.session_state.questions:
                if st.button("Очистити результати"):
                    st.session_state.ai_summary = ""
                    st.session_state.questions = ""
                    st.rerun()
                    # Очищує результати та перезапускає сторінку

        st.divider()

        if st.button("Зберегти результати в БД", type="primary"):
            if not (st.session_state.ai_summary or st.session_state.questions):
                st.warning("Спочатку згенеруйте AI результати")
            else:
                save_analysis(
                    file.name,
                    raw_text,
                    keywords,
                    summary,
                    st.session_state.ai_summary,
                    st.session_state.questions
                )
                st.success("Успішно збережено в базу даних!")
                # Зберігає результати аналізу у БД


# РЕЖИМ НАВЧАННЯ

elif mode == "Навчання":
    # Режим проходження тестів

    st.subheader("Інтерактивне тестування")

    if not st.session_state.questions:
        st.info("Спочатку згенеруйте тест у вкладці 'Аналіз тексту' або відкрийте з історії.")
    else:
        try:
            questions_data = json.loads(st.session_state.questions)
            # Парсить JSON із питаннями

            with st.form("quiz_form"):
                user_answers = {}

                for i, q in enumerate(questions_data):
                    question_text = q.get('question', 'Питання')
                    st.markdown(f"**{i + 1}. {question_text}**")

                    options = q.get("options", []).copy()

                    if options:
                        r = random.Random(question_text)
                        r.shuffle(options)
                        # Перемішує варіанти відповідей

                        safe_key = f"q_{i}_{question_text[:10]}"

                        user_answers[i] = st.radio(
                            "Оберіть варіант",
                            options,
                            key=safe_key,
                            label_visibility="collapsed"
                        )
                    else:
                        st.warning("Немає варіантів відповіді")

                    st.divider()

                submitted = st.form_submit_button("Перевірити всі відповіді", type="primary")

                if submitted:
                    score = 0
                    for i, q in enumerate(questions_data):
                        correct = str(q.get("correct", "")).strip().lower()
                        user_ans = str(user_answers.get(i, "")).strip().lower()
                        if user_ans == correct:
                            st.success(f"Питання {i + 1}: Правильно!")
                            score += 1
                        else:
                            st.error(f"Питання {i + 1}: Помилка. Правильна відповідь: {q.get('correct')}")

                    st.session_state.score = score
                    st.info(f"Твій результат: {score} з {len(questions_data)}")
                    # Обчислює та відображає результат тесту

            st.divider()
            if st.button("Завершити та очистити сторінку", use_container_width=True):
                st.session_state.questions = ""
                st.session_state.score = None
                st.rerun()
                # Очищує стан після завершення тесту

        except json.JSONDecodeError:
            st.error("Помилка формату тесту (Нейромережа не повернула чистий JSON).")
            with st.expander("Показати сиру відповідь ШІ"):
                st.write(st.session_state.questions)
            if st.button("Перегенерувати тест"):
                st.session_state.questions = ""
                st.rerun()
                # Дає можливість перегенерувати тест у разі помилки


# ІСТОРІЯ АНАЛІЗІВ

elif mode == "Історія аналізів":
    # Режим перегляду та керування історією

    col_search, col_empty, col_clear = st.columns([2, 1, 1])
    with col_search:
        search = st.text_input("Пошук за назвою або ключовими словами").lower()

    with col_clear:
        if st.button("Очистити всю історію", use_container_width=True):
            st.session_state.confirm_delete_all = True

    if st.session_state.confirm_delete_all:
        st.warning("Ви впевнені, що хочете видалити ВСЮ історію? Цю дію неможливо скасувати.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Так, видалити все", type="primary", use_container_width=True):
                clear_history()
                st.session_state.confirm_delete_all = False
                st.session_state.selected_analysis = None
                st.success("Історію очищено")
                st.rerun()
        with c2:
            if st.button("Скасувати", use_container_width=True):
                st.session_state.confirm_delete_all = False
                st.rerun()

    history = get_history()
    # Отримує всі збережені аналізи

    if search:
        history = [item for item in history if
                   search in item[1].lower() or search in item[2].lower() or search in item[3].lower()]
        # Фільтрує історію за пошуковим запитом

    if not history:
        st.info("Немає збережених аналізів.")
    else:
        for item in history:
            with st.container(border=True):
                col1, col2, col3 = st.columns([6, 1, 1])
                with col1:
                    preview = item[2][:120].replace("\n", " ") + "..."
                    st.markdown(f"📄 **{item[1]}**")
                    st.caption(f"Аналіз #{item[0]} • Дата: {item[7]}")
                    st.write(preview)
                    # Відображає короткий прев'ю аналізу

                with col2:
                    if st.button("Відкрити", key=f"open_{item[0]}", use_container_width=True):
                        st.session_state.selected_analysis = item
                        # Завантажує вибраний аналіз

                with col3:
                    if st.button("Видалити", key=f"del_{item[0]}", use_container_width=True):
                        delete_analysis(item[0])
                        if st.session_state.selected_analysis and st.session_state.selected_analysis[0] == item[0]:
                            st.session_state.selected_analysis = None
                        st.rerun()
                        # Видаляє запис із БД

# ======================
# ПЕРЕГЛЯД ОБРАНОГО АНАЛІЗУ
# ======================
if st.session_state.selected_analysis and mode == "Історія аналізів":
    # Відображає деталі обраного аналізу
    item = st.session_state.selected_analysis
    st.divider()

    with st.container(border=True):
        st.markdown(f"### 📄 Файл: {item[1]}")
        st.caption(f"Деталі аналізу #{item[0]} • {item[7]}")

        st.markdown("#### Ключові слова")
        st.info(item[3])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Класичний конспект")
            st.write(item[4])
        with col2:
            st.markdown("#### AI Конспект")
            st.write(item[5] if item[5] else "Не згенеровано")
        # Показує результати аналізу

        if item[6]:
            st.divider()
            st.markdown("#### Тестові питання")
            if st.button("Пройти тест за цим матеріалом", type="primary"):
                st.session_state.questions = item[6]
                st.success("Тест завантажено! Перейдіть у вкладку 'Навчання' в бічному меню.")
                # Завантажує тест у режим навчання

        st.divider()

        export_text = f"Файл: {item[1]}\nАналіз #{item[0]}\nДата: {item[7]}\n\nКлючові слова:\n{item[3]}\n\nКласичний конспект:\n{item[4]}\n\nAI Конспект:\n{item[5]}\n\nПитання:\n{item[6]}"
        # Формує текст для експорту

        col_dl, col_close, _ = st.columns([1.5, 1.5, 3])
        with col_dl:
            st.download_button("Завантажити TXT", data=export_text, file_name=f"analysis_{item[0]}.txt",
                               mime="text/plain", use_container_width=True)
            # Дозволяє завантажити аналіз як TXT файл

        with col_close:
            if st.button("Закрити перегляд", use_container_width=True):
                st.session_state.selected_analysis = None
                st.rerun()
                # Закриває перегляд аналізу