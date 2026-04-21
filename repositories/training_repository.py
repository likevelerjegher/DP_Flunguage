class TrainingRepository:
    def __init__(self):
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