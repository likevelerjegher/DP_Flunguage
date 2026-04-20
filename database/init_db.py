import sqlite3


def init_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # 📘 словари
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dictionaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT
    )
    """)

    # 📗 слова
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original TEXT NOT NULL,
        translation TEXT NOT NULL,
        transcription TEXT,
        language TEXT,
        difficulty INTEGER DEFAULT 1,
        correct_count INTEGER DEFAULT 0,
        wrong_count INTEGER DEFAULT 0
    )
    """)

    # 🔗 связь many-to-many
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dictionary_words (
        dictionary_id INTEGER,
        word_id INTEGER,
        PRIMARY KEY (dictionary_id, word_id),
        FOREIGN KEY(dictionary_id) REFERENCES dictionaries(id) ON DELETE CASCADE,
        FOREIGN KEY(word_id) REFERENCES words(id) ON DELETE CASCADE
    )
    """)

    # 📊 тренировки
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS training_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dictionary_id INTEGER,
        date TEXT,
        score INTEGER,
        duration INTEGER
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database created successfully")