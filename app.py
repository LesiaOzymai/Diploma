import streamlit as st
from parser import extract_text
from preprocessing import clean_text
from keywords import extract_keywords
from summarizer import summarize_text
from ai_module import generate_summary, generate_questions, safe_generate
from db import init_db, save_analysis, get_history, delete_analysis

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

# БІЧНА ПАНЕЛЬ
with st.sidebar:
    st.markdown("### Навігація")
    mode = st.radio("Оберіть розділ:", ["Аналіз тексту", "Історія аналізів"], label_visibility="collapsed")
    st.divider()
    st.caption("AI Educational System v1.0")

# ЗАГОЛОВОК
st.markdown("""
<h1 style='font-size:36px; margin-bottom: 0;'>AI Text Analyzer</h1>
<p style='color:gray; font-size:16px;'>Інтелектуальна система обробки навчальних матеріалів</p>
""", unsafe_allow_html=True)
st.divider()

# РЕЖИМ АНАЛІЗУ
if mode == "Аналіз тексту":

    file = st.file_uploader("Завантажте файл (PDF або TXT)", type=['pdf', 'txt'])

    if file is not None:
        raw_text = extract_text(file)
        clean = clean_text(raw_text)

        keywords = extract_keywords(clean)
        summary = summarize_text(clean)

        MAX_CHARS = min(len(raw_text), 15000)
        text_for_ai = raw_text[:MAX_CHARS]

        tab1, tab2 = st.tabs(["Класичний NLP", "AI Аналіз (Groq)"])

        with tab1:
            st.markdown("#### Ключові слова")
            st.info(", ".join(keywords))

            st.markdown("#### Класичний конспект")
            st.text_area("Екстрактивна сумаризація", summary, height=250)

        with tab2:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Генерувати AI Конспект", use_container_width=True):
                    with st.spinner("ШІ аналізує текст..."):
                        st.session_state.ai_summary = safe_generate(
                            generate_summary, text_for_ai, keywords
                        )

            with col2:
                if st.button("Генерувати Тести", use_container_width=True):
                    with st.spinner("ШІ створює питання..."):
                        st.session_state.questions = safe_generate(
                            generate_questions, text_for_ai
                        )

            res_col1, res_col2 = st.columns(2)

            with res_col1:
                if st.session_state.ai_summary:
                    st.markdown("#### AI Конспект")
                    st.write(st.session_state.ai_summary)

            with res_col2:
                if st.session_state.questions:
                    st.markdown("#### Тестові питання")
                    st.write(st.session_state.questions)

        st.divider()

        if st.button("Зберегти результати", type="primary"):
            if not st.session_state.ai_summary and not st.session_state.questions:
                st.warning("Спочатку згенеруйте AI конспект або тести, щоб зберегти аналіз.")
            else:
                save_analysis(
                    raw_text,
                    keywords,
                    summary,
                    st.session_state.ai_summary,
                    st.session_state.questions
                )
                st.success("Успішно збережено в базу даних!")

# РЕЖИМ ІСТОРІЇ
elif mode == "Історія аналізів":

    col_search, _ = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("Пошук за ключовими словами...", placeholder="Введіть слово...").lower()

    history = get_history()

    if search_query:
        history = [item for item in history if search_query in item[2].lower()]

    if not history:
        st.info("Історія порожня або за вашим запитом нічого не знайдено.")
    else:
        for item in history:
            with st.container():
                col1, col2, col3 = st.columns([6, 1, 1])

                with col1:
                    preview = item[1][:120].replace('\n', ' ') + "..."
                    st.markdown(
                        f"**Аналіз #{item[0]}** &nbsp;&nbsp; <span style='color:gray; font-size:14px;'>{item[6]}</span>",
                        unsafe_allow_html=True)
                    st.caption(f"Текст: {preview}")

                with col2:
                    if st.button("Відкрити", key=f"open_{item[0]}", use_container_width=True):
                        st.session_state.selected_analysis = item

                with col3:
                    if st.button("Видалити", key=f"del_{item[0]}", use_container_width=True):
                        delete_analysis(item[0])
                        st.rerun()

                st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

# ПЕРЕГЛЯД ОБРАНОГО АНАЛІЗУ
if st.session_state.selected_analysis and mode == "Історія аналізів":
    item = st.session_state.selected_analysis

    st.markdown(f"### Деталі аналізу #{item[0]}")

    st.markdown("#### Ключові слова")
    st.info(item[2])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Класичний конспект")
        st.write(item[3])
    with col2:
        st.markdown("#### AI Конспект")
        st.write(item[4] if item[4] else "Не генерувалося")

    st.markdown("#### Тестові питання")
    st.write(item[5] if item[5] else "Не генерувалися")

    st.divider()

    export_text = f"Аналіз #{item[0]}\nДата: {item[6]}\n\nКлючові слова: {item[2]}\n\nКласичний конспект:\n{item[3]}\n\nAI Конспект:\n{item[4]}\n\nТести:\n{item[5]}\n"

    col_dl, col_close, _ = st.columns([1.5, 1.5, 3])
    with col_dl:
        st.download_button("Завантажити TXT", data=export_text, file_name=f"analysis_{item[0]}.txt", mime="text/plain",
                           use_container_width=True)
    with col_close:
        if st.button("Закрити перегляд", use_container_width=True):
            st.session_state.selected_analysis = None
            st.rerun()