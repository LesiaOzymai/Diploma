import streamlit as st
from parser import extract_text
from preprocessing import clean_text
from keywords import extract_keywords
from summarizer import summarize_text
from ai_module import generate_summary, generate_questions, safe_generate
from db import init_db, save_analysis, get_history, delete_analysis, clear_history

st.set_page_config(
    page_title="AI Text Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# SESSION STATE
if "selected_analysis" not in st.session_state:
    st.session_state.selected_analysis = None
if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = ""
if "questions" not in st.session_state:
    st.session_state.questions = ""
if "confirm_delete_all" not in st.session_state:
    st.session_state.confirm_delete_all = False

# SIDEBAR
with st.sidebar:
    st.title("AI Text Analyzer")
    st.caption("Educational NLP System")

    mode = st.radio(
        "Navigation",
        ["Аналіз тексту", "Історія"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("v1.0")

# HEADER
st.title("AI Text Analyzer")
st.caption("Система аналізу навчальних матеріалів із використанням NLP та AI")
st.divider()

# ======================
# АНАЛІЗ ТЕКСТУ
# ======================
if mode == "Аналіз тексту":

    with st.container(border=True):
        st.subheader("Завантаження файлу")

        file = st.file_uploader(
            "Оберіть PDF або TXT файл",
            type=["pdf", "txt"]
        )

        if file is not None:
            st.caption(f"{file.name} • {round(file.size / 1024, 2)} KB")

    if file is not None:
        try:
            raw_text = extract_text(file)
        except ValueError:
            st.error("Файл пошкоджений або не є PDF/TXT")
            st.stop()

        clean = clean_text(raw_text)

        keywords = extract_keywords(clean)
        summary = summarize_text(clean)

        MAX_CHARS = min(len(raw_text), 15000)
        text_for_ai = raw_text[:MAX_CHARS]

        tab1, tab2 = st.tabs(["Класичний NLP", "AI Аналіз"])

        # CLASSIC
        with tab1:
            with st.container(border=True):
                st.subheader("Ключові слова")
                st.write(", ".join(keywords))

            with st.container(border=True):
                st.subheader("Класичний конспект")
                st.text_area("Summary", summary, height=250)

        # AI
        with tab2:
            with st.container(border=True):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "Згенерувати AI конспект",
                        use_container_width=True,
                        disabled=bool(st.session_state.ai_summary)
                    ):
                        with st.spinner("Генерація..."):
                            st.session_state.ai_summary = safe_generate(
                                generate_summary,
                                text_for_ai,
                                keywords
                            )

                with col2:
                    if st.button(
                        "Згенерувати питання",
                        use_container_width=True,
                        disabled=bool(st.session_state.questions)
                    ):
                        with st.spinner("Генерація..."):
                            st.session_state.questions = safe_generate(
                                generate_questions,
                                text_for_ai
                            )

            col1, col2 = st.columns(2)

            with col1:
                if st.session_state.ai_summary:
                    with st.container(border=True):
                        st.subheader("AI конспект")
                        st.write(st.session_state.ai_summary)

            with col2:
                if st.session_state.questions:
                    with st.container(border=True):
                        st.subheader("Питання")
                        st.write(st.session_state.questions)

            if st.session_state.ai_summary or st.session_state.questions:
                if st.button("Очистити результати"):
                    st.session_state.ai_summary = ""
                    st.session_state.questions = ""
                    st.rerun()

        st.divider()

        if st.button("Зберегти результати", type="primary"):
            if not (st.session_state.ai_summary or st.session_state.questions):
                st.warning("Спочатку згенеруйте AI результати")
            else:
                save_analysis(
                    raw_text,
                    keywords,
                    summary,
                    st.session_state.ai_summary,
                    st.session_state.questions
                )
                st.success("Збережено")

# ======================
# ІСТОРІЯ
# ======================
elif mode == "Історія":

    st.subheader("Історія аналізів")

    col1, col2 = st.columns([3, 1])

    with col1:
        search = st.text_input("Пошук за ключовими словами").lower()

    with col2:
        if st.button("Очистити всю історію", use_container_width=True):
            st.session_state.confirm_delete_all = True

    # ПІДТВЕРДЖЕННЯ
    if st.session_state.confirm_delete_all:
        st.warning("Ви впевнені, що хочете видалити ВСЮ історію?")

        col_yes, col_no = st.columns(2)

        with col_yes:
            if st.button("Так, видалити", type="primary", use_container_width=True):
                clear_history()
                st.session_state.confirm_delete_all = False
                st.session_state.selected_analysis = None
                st.success("Історію очищено")
                st.rerun()

        with col_no:
            if st.button("Скасувати", use_container_width=True):
                st.session_state.confirm_delete_all = False
                st.rerun()

    history = get_history()

    if search:
        history = [
            item for item in history
            if search in item[2].lower()
        ]

    if not history:
        st.info("Немає даних")
    else:
        for item in history:

            with st.container(border=True):
                col1, col2, col3 = st.columns([6, 1, 1])

                with col1:
                    preview = item[1][:120].replace("\n", " ") + "..."
                    st.markdown(f"**Аналіз #{item[0]}**")
                    st.caption(item[6])
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
# ПЕРЕГЛЯД
# ======================
if st.session_state.selected_analysis and mode == "Історія":

    item = st.session_state.selected_analysis

    st.divider()

    with st.container(border=True):
        st.subheader(f"Аналіз #{item[0]}")

        st.markdown("#### Ключові слова")
        st.write(item[2])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Класичний конспект")
            st.write(item[3])

        with col2:
            st.markdown("#### AI конспект")
            st.write(item[4] if item[4] else "Не згенеровано")

        st.markdown("#### Питання")
        st.write(item[5] if item[5] else "Не згенеровано")

        st.divider()

        export_text = f"""Аналіз #{item[0]}
Дата: {item[6]}

Ключові слова:
{item[2]}

Класичний конспект:
{item[3]}

AI конспект:
{item[4]}

Питання:
{item[5]}
"""

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Завантажити TXT",
                data=export_text,
                file_name=f"analysis_{item[0]}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            if st.button("Закрити", use_container_width=True):
                st.session_state.selected_analysis = None
                st.rerun()