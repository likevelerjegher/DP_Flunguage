from datetime import datetime

class TrainingRepository:
    def __init__(self, storage):
        self.storage = storage
        self.sessions = []
        self.results = []

    def save_session(self, session):
        self.sessions.append(session)

    def save_result(self, result):
        self.results.append(result)

    def save_response_time(self, word_id, time_sec, is_correct):
        self.storage.execute("""
            INSERT INTO training_stats (word_id, time_sec, is_correct, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (word_id, time_sec, int(is_correct)))

    def create_session(self, dictionary_id):
        cursor = self.storage.conn.cursor()

        cursor.execute("""
            INSERT INTO training_sessions (dictionary_id, date, score, duration)
            VALUES (?, ?, 0, 0)
        """, (
            dictionary_id,
            datetime.now().isoformat()
        ))

        self.storage.conn.commit()
        return cursor.lastrowid

    def save_stat(self, session_id, word_id, is_correct, time_spent):
        self.storage.execute("""
            INSERT INTO training_stats (session_id, word_id, time_sec, is_correct, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            word_id,
            time_spent,
            int(is_correct),
            datetime.now().isoformat()
        ))

    def finish_session(self, session_id, words_count, score, duration):
        self.storage.execute("""
            UPDATE training_sessions
            SET words_count = ?, score = ?, duration = ?
            WHERE id = ?
        """, (words_count, score, duration, session_id))

    def get_general_stats(self):
        cursor = self.storage.conn.cursor()

        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(is_correct) as correct,
                AVG(time_sec) as avg_time
            FROM training_stats
        """)

        total, correct, avg_time = cursor.fetchone()

        correct = correct or 0
        avg_time = avg_time or 0

        accuracy = int((correct / total) * 100) if total else 0

        return {
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "avg_time": round(avg_time, 2)
        }

    def get_last_sessions(self, limit=10):
        cursor = self.storage.conn.cursor()

        cursor.execute("""
            SELECT id, date, words_count, score, duration
            FROM training_sessions
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

    def get_hard_words(self, limit=10):
        cursor = self.storage.conn.cursor()

        cursor.execute("""
            SELECT 
                original,
                wrong_count,
                CASE 
                    WHEN (correct_count + wrong_count) = 0 THEN 0
                    ELSE (correct_count * 100) / (correct_count + wrong_count)
                END as success_rate
            FROM words
            ORDER BY wrong_count DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

    def update_word_stats(self, word_id, correct_count, wrong_count):
        cursor = self.storage.conn.cursor()

        cursor.execute("""
            UPDATE words
            SET correct_count = ?, wrong_count = ?
            WHERE id = ?
        """, (correct_count, wrong_count, word_id))

        self.storage.conn.commit()

    def delete_session(self, session_id):
        cursor = self.storage.conn.cursor()

        cursor.execute("DELETE FROM training_stats WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM training_sessions WHERE id = ?", (session_id,))

        self.storage.conn.commit()

        self.recalc_all_stats()

    def get_global_stats(self):
        cursor = self.storage.conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_answers,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                AVG(time_spent) as avg_time
            FROM training_stats
        """)

        return cursor.fetchone()

    def recalc_all_stats(self):
        cursor = self.storage.conn.cursor()

        # 1. пересчитать words
        cursor.execute("""
            UPDATE words
            SET correct_count = (
                SELECT COALESCE(SUM(is_correct), 0)
                FROM training_stats
                WHERE training_stats.word_id = words.id
            ),
            wrong_count = (
                SELECT COALESCE(SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END), 0)
                FROM training_stats
                WHERE training_stats.word_id = words.id
            )
        """)

        self.storage.conn.commit()