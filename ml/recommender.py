import numpy as np
import json


class WordRecommender:
    def __init__(self):
        self.embeddings = np.load("ml/embeddings.npy")

        with open("ml/vocab.json", "r", encoding="utf-8") as f:
            self.vocab = json.load(f)

        self.index_to_word = {i: w for w, i in self.vocab.items()}

    # =========================
    # CORE RECOMMENDATION
    # =========================

    def recommend(self, good_words, bad_words, top_n=10):
        """
        good_words → то, что пользователь знает
        bad_words → где он ошибается
        """

        if not good_words:
            return []

        user_vector = self._build_user_vector(good_words, bad_words)

        scored = []

        for i, emb in enumerate(self.embeddings):
            word = self.index_to_word[i]

            # не рекомендуем уже изученное
            if word in good_words:
                continue

            # базовая похожесть
            sim = self._cosine(user_vector, emb)

            # усиление: если слово похоже на "ошибочные" — поднимаем приоритет
            error_boost = self._error_boost(word, bad_words)

            score = sim + error_boost

            scored.append((word, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [w for w, _ in scored[:top_n]]

    # =========================
    # USER VECTOR
    # =========================

    def _build_user_vector(self, good_words, bad_words):
        vectors = []

        # хорошие слова дают “правильное знание”
        for w in good_words:
            vec = self._get_vector(w)
            if vec is not None:
                vectors.append(vec)

        if not vectors:
            return np.zeros(self.embeddings.shape[1])

        return np.mean(vectors, axis=0)

    # =========================
    # ERROR BOOSTING
    # =========================

    def _error_boost(self, word, bad_words):
        """
        Если слово похоже на ошибочные — повышаем шанс рекомендации
        """

        if not bad_words:
            return 0

        word_vec = self._get_vector(word)
        if word_vec is None:
            return 0

        similarities = []

        for w in bad_words:
            vec = self._get_vector(w)
            if vec is not None:
                similarities.append(self._cosine(word_vec, vec))

        if not similarities:
            return 0

        # если похоже на ошибки → даём небольшой буст
        return max(similarities) * 0.2

    # =========================
    # VECTOR ACCESS
    # =========================

    def _get_vector(self, word):
        idx = self.vocab.get(word)
        if idx is None:
            return None
        return self.embeddings[idx]

    def _pos_bonus(self, word, good_words, word_meta):
        # если часть речи совпадает — плюс
        return 0.1

    # =========================
    # COSINE
    # =========================

    def _cosine(self, a, b):
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0
        return np.dot(a, b) / denom