import random
from datetime import datetime


class TrainingService:
    def __init__(self, word_service, dict_service, repo):
        self.word_service = word_service
        self.dict_service = dict_service
        self.repo = repo

        self.session = None
        self.words_queue = []

    def start_session(self, mode, source_type, source_id, limit, use_stats=False):
        self.session = {
            "mode": mode,
            "source_type": source_type,
            "source_id": source_id,
            "limit": limit,
            "correct": 0,
            "completed": 0
        }

        if source_type == "all":
            words = self.word_service.get_all_words()
        else:
            words = self.dict_service.get_words(source_id)

        random.shuffle(words)
        limit = min(limit, len(words))
        self.words_queue = words[:limit]
        self.use_stats = use_stats

    def get_next_task(self):
        if not self.words_queue:
            return None

        word = self.words_queue.pop(0)

        mode = self.session["mode"]
        if mode == "mixed":
            mode = random.choice(["input", "choice"])

        if mode == "input":
            return {
                "mode": "input",
                "word": word,
                "question": word["original"],
                "answer": word["translation"]
            }

        options = self._generate_options(word)

        return {
            "mode": "choice",
            "word": word,
            "question": word["original"],
            "answer": word["translation"],
            "options": options
        }

    def _generate_options(self, correct_word):
        all_words = self.word_service.get_all_words()

        variants = [w["translation"] for w in all_words if w["id"] != correct_word["id"]]
        wrong = random.sample(variants, min(3, len(variants)))

        options = wrong + [correct_word["translation"]]
        random.shuffle(options)

        return options

    def check_answer(self, task, answer):
        correct = task["answer"].lower().strip()
        user = answer.lower().strip()

        is_correct = correct == user

        self.session["completed"] += 1
        if is_correct:
            self.session["correct"] += 1

        return is_correct

    def update_word(self, word, is_correct: bool):
        # простая версия (потом заменим на нейронку)

        if is_correct:
            word["correct_count"] = word.get("correct_count", 0) + 1
        else:
            word["wrong_count"] = word.get("wrong_count", 0) + 1

    def update_progress(self, word, is_correct):
        if is_correct:
            word["correct"] = word.get("correct", 0) + 1
        else:
            word["wrong"] = word.get("wrong", 0) + 1

        # в будущем тут будет ML логика