import random
from datetime import datetime


class TrainingService:
    def __init__(self, word_service, dict_service, repo):
        self.word_service = word_service
        self.dict_service = dict_service
        self.repo = repo

        self.session = None
        self.words_queue = []

    def start_session(self, mode, source_type, source_id, limit, use_stats):
        # ===== слова =====
        if source_type == "all":
            words = self.word_service.get_all_words()
        else:
            words = self.dict_service.get_words(source_id)

        if not words:
            self.words_queue = []
            return

        random.shuffle(words)
        limit = min(limit, len(words))
        self.words_queue = words[:limit]

        # ===== сессия =====
        session_id = None
        if use_stats:
            session_id = self.repo.create_session(source_id)

        self.session = {
            "mode": mode,
            "source_type": source_type,
            "source_id": source_id,
            "limit": limit,
            "completed": 0,
            "correct": 0,
            "use_stats": use_stats,
            "started_at": datetime.now(),
            "session_id": session_id
        }

    def get_next_task(self):
        if not self.words_queue:
            return None

        word = self.words_queue.pop(0)

        # 👉 считаем здесь, а не в UI
        self.session["completed"] += 1

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

        return is_correct

    def update_word(self, word, is_correct: bool):
        # простая версия (потом заменим на нейронку)

        if is_correct:
            word["correct_count"] = word.get("correct_count", 0) + 1
        else:
            word["wrong_count"] = word.get("wrong_count", 0) + 1

    def update_progress(self, word, is_correct, time_spent):
        if is_correct:
            self.session["correct"] += 1

        correct_count = word["correct_count"] if "correct_count" in word.keys() else 0
        wrong_count = word["wrong_count"] if "wrong_count" in word.keys() else 0

        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1

        if self.repo:
            self.repo.update_word_stats(
                word["id"],
                correct_count,
                wrong_count
            )

        if self.repo and self.session["use_stats"]:
            self.repo.save_stat(
                self.session["session_id"],
                word["id"],
                is_correct,
                time_spent
            )

    def finish_session(self):
        if not self.session["use_stats"]:
            return

        duration = (datetime.now() - self.session["started_at"]).seconds
        total = self.session["limit"]
        correct = self.session["correct"]

        score = int((correct / total) * 100) if total else 0

        self.repo.finish_session(
            self.session["session_id"],
            total,
            score,
            duration
        )