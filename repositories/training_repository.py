from datetime import datetime

class TrainingRepository:
    def __init__(self, storage):
        self.storage = storage
        self.sessions = []
        self.results = []
        self.training_service = None

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

    def finish_session(self, session_id, words_count, score, duration, mode):
        self.storage.execute("""
            UPDATE training_sessions
            SET words_count = ?, score = ?, duration = ?, mode = ?
            WHERE id = ?
        """, (words_count, score, duration, mode, session_id))

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
            SELECT id, date, mode, words_count, score, duration
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

        cursor.execute("DELETE FROM word_history WHERE session_id = ?", (session_id,))
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

    def get_word_groups_stats(self):
        cursor = self.storage.conn.cursor()
        rows = cursor.execute("SELECT id FROM words").fetchall()

        new = good = medium = bad = 0

        for (word_id,) in rows:

            history = self.get_answers_count(word_id)

            if history == 0:
                new += 1
                continue

            recent = self.get_recent_answers(word_id, 20)

            correct = sum(recent)
            total = len(recent)

            accuracy = correct / total if total else 0

            if total < 5 or accuracy < 0.6:
                bad += 1
            elif accuracy >= 0.85 and total >= 10:
                good += 1
            else:
                medium += 1

        return {
            "new": new,
            "good": good,
            "medium": medium,
            "bad": bad
        }

    def get_words_with_status(self, limit=50):
        cursor = self.storage.conn.cursor()
        rows = cursor.execute("SELECT * FROM words").fetchall()

        result = []

        for w in rows:
            w = dict(w)

            correct = int(w.get("correct_count") or 0)
            wrong = int(w.get("wrong_count") or 0)
            total = correct + wrong

            history = self.get_answers_count(w["id"])

            if history == 0:
                status = "new"
            else:
                recent = self.get_recent_answers(w["id"], 20)

                correct = sum(recent)
                total = len(recent)

                accuracy = correct / total if total else 0

                if total < 5 or accuracy < 0.6:
                    status = "bad"
                elif accuracy >= 0.85 and total >= 10:
                    status = "good"
                else:
                    status = "medium"

            result.append((
                w.get("original"),
                wrong,
                status
            ))

        result.sort(key=lambda x: x[1], reverse=True)
        return result[:limit]

    def get_words_count(self):
        cursor = self.storage.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words")
        return cursor.fetchone()[0]

    def save_word_history(self, word_id, is_correct, session_id=None):
        self.storage.conn.execute("""
            INSERT INTO word_history (word_id, session_id, is_correct, answered_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (word_id, session_id, int(is_correct)))

        self.storage.conn.commit()

    def get_recent_answers(self, word_id, limit=5):
        rows = self.storage.conn.execute("""
            SELECT is_correct
            FROM word_history
            WHERE word_id = ?
            ORDER BY answered_at DESC
            LIMIT ?
        """, (word_id, limit)).fetchall()

        return [r[0] for r in rows]

    def get_answers_count(self, word_id):
        cursor = self.storage.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM word_history
            WHERE word_id = ?
        """, (word_id,))
        return cursor.fetchone()[0] or 0
