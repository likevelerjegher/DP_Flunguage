import random
from datetime import datetime
from ml.recommender import WordRecommender


class TrainingService:
    def __init__(self, word_service, dict_service, repo):
        self.word_service = word_service
        self.dict_service = dict_service
        self.repo = repo

        self.session = None
        self.words_queue = []
        self.recommender = WordRecommender()

    def start_session(self, mode, source_type, source_id, limit, use_stats, status="all"):

        words = [dict(w) for w in self._load_words(source_type, source_id)]

        has_progress = any(
            self.repo.get_answers_count(w["id"]) > 0
            for w in words
        ) if self.repo else False

        if not has_progress:
            status = "new"

        words = self._apply_status_filter(words, status)

        if len(words) < 2:
            return False

        random.shuffle(words)

        limit = min(limit, len(words))
        self.words_queue = words[:limit]

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
            "session_id": session_id,
            "status_filter": status
        }

        return True

    def get_word_status(self, word):
        word = dict(word)

        word_id = word.get("id")
        if word_id is None:
            return "medium"

        history_count = self.repo.get_answers_count(word_id) if self.repo else 0
        if history_count == 0:
            return "new"

        correct = int(word.get("correct_count") or 0)
        wrong = int(word.get("wrong_count") or 0)
        total = correct + wrong

        if total == 0:
            return "new"

        accuracy = correct / total

        recent = self.repo.get_recent_answers(word_id) if self.repo else []
        recent = recent[-5:]
        recent_score = sum(recent) / len(recent) if recent else accuracy

        if total < 3:
            if accuracy >= 0.6:
                return "medium"
            return "bad"

        if accuracy >= 0.8 and total >= 5 and recent_score >= 0.8:
            return "good"

        if accuracy >= 0.6:
            return "medium"

        return "bad"

    def get_next_task(self):
        if not self.words_queue:
            return None

        word = self.words_queue.pop(0)

        # считаем здесь, а не в UI
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
        word.setdefault("correct_count", 0)
        word.setdefault("wrong_count", 0)
        recent = word.setdefault("recent_answers", [])

        if is_correct:
            word["correct_count"] += 1
            recent.append(1)
        else:
            word["wrong_count"] += 1
            recent.append(0)

        word["recent_answers"] = recent[-10:]

    def update_progress(self, word, is_correct, time_spent):
        if self.session and is_correct:
            self.session["correct"] += 1

        self.update_word(word, is_correct)

        self.repo.save_word_history(
            word["id"],
            is_correct,
            self.session["session_id"] if self.session else None
        )

        self.repo.update_word_stats(
            word["id"],
            word["correct_count"],
            word["wrong_count"]
        )

        if self.session and self.session["use_stats"]:
            self.repo.save_stat(
                self.session["session_id"],
                word["id"],
                is_correct,
                time_spent
            )

    def finish_session(self):
        if not self.session:
            return

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
            duration,
            self.session["mode"]
        )

    def get_filtered_words(self, source_type, source_id, status="all"):
        if source_type == "all":
            words = self.word_service.get_all_words()
        else:
            words = self.dict_service.get_words(source_id)

        if status != "all":
            words = [w for w in words if self.get_word_status(w) == status]

        return words

    def _load_words(self, source_type, source_id):
        if source_type == "all":
            return self.word_service.get_all_words()
        else:
            return self.dict_service.get_words(source_id)

    def _apply_status_filter(self, words, status):
        if status == "all":
            return words

        result = []

        for w in words:
            w_dict = dict(w)
            if self.get_word_status(w_dict) == status:
                result.append(w)

        return result

    def _to_dict(self, word):
        return dict(word)

    def normalize_translation(self, w):
        tr = w.get("translations") or w.get("translation") or []

        if isinstance(tr, str):
            tr = [tr]

        return tr

    def get_recommended_words(self, limit=15):
        good_words, bad_words = self.get_recommendation_data()

        recommended_words = self.recommender.recommend(
            good_words,
            bad_words,
            top_n=limit
        )

        print("RECOMMENDED RAW:", recommended_words)

        all_words = self.word_service.get_all_words()

        db_index = {}

        for w in all_words:

            w = dict(w)  #FIX SQLITE ROW -> dict

            key1 = (w.get("original") or "").lower().strip()
            key2 = (w.get("word") or "").lower().strip()

            if key1:
                db_index[key1] = w

            if key2:
                db_index[key2] = w

        result = []

        for w in recommended_words:
            word_norm = w.strip().lower()

            if word_norm in db_index:
                db_word = db_index[word_norm]

                translations = db_word.get("translations") or db_word.get("translation") or []
                if isinstance(translations, str):
                    translations = [translations]

                result.append({
                    "word": db_word.get("original", word_norm),
                    "translation": translations[:3]
                })
            else:
                meta = self.recommender.word_meta.get(word_norm)

                if meta:
                    result.append({
                        "word": meta["word"],
                        "translation": (meta.get("translations", []) or [])[:3]
                    })
                else:
                    result.append({
                        "word": word_norm,
                        "translation": []
                    })
        return result

    def get_recommendation_data(self):
        words = self.word_service.get_all_words()

        good = []
        bad = []

        for w in words:
            w = dict(w)  # ВАЖНО

            status = self.get_word_status(w)
            text = self.get_word_text(w)

            if not text:
                continue

            if status == "good":
                good.append({
                    "word": text,
                    "translations": self.normalize_translation(w)
                })

            elif status == "bad":
                bad.append({
                    "word": text,
                    "translations": self.normalize_translation(w)
                })

        return good, bad

    def get_word_text(self, w):
        return (w.get("word") or w.get("original") or "").lower().strip()

    def get_word_translations(self, w):
        return w.get("translations") or []