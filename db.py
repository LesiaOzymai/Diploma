import sqlite3

DB_NAME = "data.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            keywords TEXT,
            summary TEXT,
            ai_summary TEXT,
            questions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


def save_analysis(text, keywords, summary, ai_summary, questions):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO analyses (text, keywords, summary, ai_summary, questions)
        VALUES (?, ?, ?, ?, ?)
        """, (
            text,
            ", ".join(keywords),
            summary,
            ai_summary,
            questions
        ))


def get_history():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, text, keywords, summary, ai_summary, questions, created_at
        FROM analyses
        ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()

    return rows


def delete_analysis(analysis_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))