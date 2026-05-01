import sqlite3

DB_NAME = "data.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS analyses
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           file_name
                           TEXT,
                           raw_text
                           TEXT,
                           keywords
                           TEXT,
                           summary
                           TEXT,
                           ai_summary
                           TEXT,
                           questions
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       """)


def save_analysis(file_name, raw_text, keywords, summary, ai_summary, questions):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        raw_text_limited = raw_text[:5000]

        cursor.execute("""
                       INSERT INTO analyses (file_name, raw_text, keywords, summary, ai_summary, questions)
                       VALUES (?, ?, ?, ?, ?, ?)
                       """, (
                           file_name,
                           raw_text_limited,
                           ", ".join(keywords),
                           summary,
                           ai_summary,
                           questions
                       ))


def get_history():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT id,
                              file_name,
                              raw_text,
                              keywords,
                              summary,
                              ai_summary,
                              questions,
                              created_at
                       FROM analyses
                       ORDER BY created_at DESC
                       """)
        return cursor.fetchall()


def delete_analysis(analysis_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))


def clear_history():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='analyses'")