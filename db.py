import sqlite3

DB_NAME = "data.db"


def init_db():
    # Ініціалізує базу даних та створює таблицю для збереження результатів аналізу
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            raw_text TEXT,
            keywords TEXT,
            summary TEXT,
            ai_summary TEXT,
            questions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


def save_analysis(file_name, raw_text, keywords, summary, ai_summary, questions):
    # Зберігає результати аналізу тексту у базу даних з обмеженням довжини сирого тексту
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO analyses (file_name, raw_text, keywords, summary, ai_summary, questions)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            file_name,
            raw_text[:5000],  # контроль розміру БД без "..."
            ", ".join(keywords),
            summary,
            ai_summary,
            questions
        ))


def get_history():
    # Отримує історію всіх аналізів, відсортовану за датою створення (новіші зверху)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, file_name, raw_text, keywords, summary, ai_summary, questions, created_at
        FROM analyses
        ORDER BY created_at DESC
        """)
        return cursor.fetchall()


def delete_analysis(analysis_id):
    # Видаляє один запис аналізу з бази даних за його ідентифікатором
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))


def clear_history():
    # Повністю очищає історію аналізів та скидає лічильник автоінкременту
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM analyses")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='analyses'")