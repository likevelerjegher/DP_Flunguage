from datetime import datetime


class TrainingSession:
    def __init__(self, mode, source_type, source_id, limit):
        self.mode = mode              # input / choice / mixed
        self.source_type = source_type  # all / dictionary
        self.source_id = source_id
        self.limit = limit

        self.started_at = datetime.now()
        self.completed = 0
        self.correct = 0