class Word:
    def __init__(
        self,
        id=None,
        original="",
        translation="",
        transcription="",
        language="",
        difficulty=1,
        correct_count=0,
        wrong_count=0
    ):
        self.id = id
        self.original = original
        self.translation = translation
        self.transcription = transcription
        self.language = language
        self.difficulty = difficulty
        self.correct_count = correct_count
        self.wrong_count = wrong_count
