class TrainingRepository:
    def __init__(self):
        self.sessions = []
        self.results = []

    def save_session(self, session):
        self.sessions.append(session)

    def save_result(self, result):
        self.results.append(result)