import streamlit as st
import json
import random

from parser import extract_text
from preprocessing import clean_text
from keywords import extract_keywords
from summarizer import summarize_text
from ai_module import generate_summary, generate_questions, safe_generate
from db import init_db, save_analysis, get_history, delete_analysis, clear_history

# КОНФІГУРАЦІЯ
st.set_page_config(page_title="AI Text Analyzer", layout="wide", initial_sidebar_state="expanded")

# СТИЛІ
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
.stButton>button {
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

init_db()

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

# БІЧНА ПАНЕЛЬ
with st.sidebar:
    st.markdown("### Навігація")
    mode = st.radio("Оберіть розділ:", ["Аналіз тексту", "Навчання", "Історія аналізів"], label_visibility="collapsed")
    st.divider()
    st.caption("AI Educational System v1.0")

# ЗАГОЛОВОК
st.markdown("""
<h1 style='font-size:36px; margin-bottom: 0;'>AI Text Analyzer</h1>
<p style='color:gray; font-size:16px;'>Система аналізу навчальних матеріалів із використанням NLP та AI</p>
""", unsafe_allow_html=True)
st.divider()

# ======================
# РЕЖИМ АНАЛІЗУ
# ======================
if mode == "Аналіз тексту":

    with st.container(border=True):
        st.subheader("Завантаження файлу")
        file = st.file_uploader("Оберіть PDF або TXT файл", type=["pdf", "txt"])

        if file is not None:
            st.caption(f"Файл: {file.name} • Розмір: {round(file.size / 1024, 2)} KB")

    if file is not None:
        try:
            raw_text = extract_text(file)
        except Exception:
            st.error("Файл пошкоджений або не читається. Спробуйте інший.")
            st.stop()

        clean = clean_text(raw_text)
        keywords = extract_keywords(clean)
        summary = summarize_text(clean)

        MAX_CHARS = min(len(raw_text), 15000)
        text_for_ai = raw_text[:MAX_CHARS]

        tab1, tab2 = st.tabs(["Класичний NLP", "AI Аналіз (Groq)"])

        with tab1:
            with st.container(border=True):
                st.markdown("#### Ключові слова")
                st.info(", ".join(keywords))

            with st.container(border=True):
                st.markdown("#### Класичний конспект")
                st.text_area("Екстрактивна сумаризація", summary, height=250)

        with tab2:
            with st.container(border=True):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Згенерувати AI конспект", use_container_width=True,
                                 disabled=bool(st.session_state.ai_summary)):
                        with st.spinner("ШІ аналізує текст..."):
                            st.session_state.ai_summary = safe_generate(generate_summary, text_for_ai, keywords)

                with col2:
                    if st.button("Згенерувати тест", use_container_width=True,
                                 disabled=bool(st.session_state.questions)):
                        with st.spinner("ШІ створює питання..."):
                            st.session_state.questions = safe_generate(generate_questions, text_for_ai)

            res_col1, res_col2 = st.columns(2)

            with res_col1:
                if st.session_state.ai_summary:
                    with st.container(border=True):
                        st.markdown("#### AI Конспект")
                        st.write(st.session_state.ai_summary)

            with res_col2:
                if st.session_state.questions:
                    with st.container(border=True):
                        st.markdown("#### Питання")
                        st.success("Тест готовий! Перейдіть у вкладку 'Навчання' в бічному меню.")

            if st.session_state.ai_summary or st.session_state.questions:
                if st.button("Очистити результати"):
                    st.session_state.ai_summary = ""
                    st.session_state.questions = ""
                    st.rerun()

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

# ======================
# РЕЖИМ НАВЧАННЯ
# ======================
elif mode == "Навчання":

    st.subheader("Інтерактивне тестування")

    if not st.session_state.questions:
        st.info("Спочатку згенеруйте тест у вкладці 'Аналіз тексту' або відкрийте з історії.")
    else:
        try:
            questions_data = json.loads(st.session_state.questions)

            with st.form("quiz_form"):
                user_answers = {}

                for i, q in enumerate(questions_data):
                    question_text = q.get('question', 'Питання')
                    st.markdown(f"**{i + 1}. {question_text}**")

                    options = q.get("options", [])

                    if options:
                        # Захист від стрибання варіантів
                        r = random.Random(question_text)
                        r.shuffle(options)

                        safe_key = f"q_{i}_{question_text[:10]}"

                        user_answers[i] = st.radio("Оберіть варіант", options, key=safe_key,
                                                   label_visibility="collapsed")
                    else:
                        st.warning("Немає варіантів відповіді")

                    st.divider()

                submitted = st.form_submit_button("Перевірити всі відповіді", type="primary")

                if submitted:
                    score = 0
                    for i, q in enumerate(questions_data):
                        correct = q.get("correct", "")
                        if user_answers.get(i) == correct:
                            st.success(f"Питання {i + 1}: Правильно!")
                            score += 1
                        else:
                            st.error(f"Питання {i + 1}: Помилка. Правильна відповідь: {correct}")

                    st.session_state.score = score
                    st.info(f"Твій результат: {score} з {len(questions_data)}")

            # Кнопка для очищення тесту
            st.divider()
            if st.button("Завершити та очистити сторінку", use_container_width=True):
                st.session_state.questions = ""
                st.session_state.score = None
                st.rerun()

        except json.JSONDecodeError:
            st.error("Помилка формату тесту (Нейромережа не повернула чистий JSON).")
            with st.expander("Показати сиру відповідь ШІ"):
                st.write(st.session_state.questions)
            if st.button("Перегенерувати тест"):
                st.session_state.questions = ""
                st.rerun()

# ======================
# ІСТОРІЯ АНАЛІЗІВ
# ======================
elif mode == "Історія аналізів":

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

    if search:
        history = [item for item in history if search in item[1].lower() or search in item[3].lower()]

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

                with col2:
                    if st.button("Відкрити", key=f"open_{item[0]}", use_container_width=True):
                        st.session_state.selected_analysis = item

                with col3:
                    if st.button("Видалити", key=f"del_{item[0]}", use_container_width=True):
                        delete_analysis(item[0])
                        if st.session_state.selected_analysis and st.session_state.selected_analysis[0] == item[0]:
                            st.session_state.selected_analysis = None
                        st.rerun()

# ======================
# ПЕРЕГЛЯД ОБРАНОГО АНАЛІЗУ
# ======================
if st.session_state.selected_analysis and mode == "Історія аналізів":
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

        if item[6]:
            st.divider()
            st.markdown("#### Тестові питання")
            if st.button("Пройти тест за цим матеріалом", type="primary"):
                st.session_state.questions = item[6]
                st.success("Тест завантажено! Перейдіть у вкладку 'Навчання' в бічному меню.")

        st.divider()

        export_text = f"Файл: {item[1]}\nАналіз #{item[0]}\nДата: {item[7]}\n\nКлючові слова:\n{item[3]}\n\nКласичний конспект:\n{item[4]}\n\nAI Конспект:\n{item[5]}\n\nПитання:\n{item[6]}"

        col_dl, col_close, _ = st.columns([1.5, 1.5, 3])
        with col_dl:
            st.download_button("Завантажити TXT", data=export_text, file_name=f"analysis_{item[0]}.txt",
                               mime="text/plain", use_container_width=True)
        with col_close:
            if st.button("Закрити перегляд", use_container_width=True):
                st.session_state.selected_analysis = None
                st.rerun()