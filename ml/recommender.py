import os

from pathlib import Path
import numpy as np
import json


class WordRecommender:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent

        self.embeddings = np.load(base_dir / "embeddings.npy")

        with open(base_dir / "vocab.json", "r", encoding="utf-8") as f:
            raw_vocab = json.load(f)

        # нормализация vocab
        self.vocab = {
            k.strip().lower(): v
            for k, v in raw_vocab.items()
        }

        self.index_to_word = {
            i: w.strip().lower()
            for w, i in self.vocab.items()
        }

        print("vocab size:", len(self.vocab))
        print("embeddings shape:", self.embeddings.shape)

    # =========================
    # CORE RECOMMENDATION
    # =========================
    def _norm(self, w: str):
        return w.strip().lower()

    def recommend(self, good_words, bad_words, top_n=10):

        good_words = self._filter_words(good_words)
        bad_words = self._filter_words(bad_words)

        if not good_words:
            return []

        user_vector = self._build_user_vector(good_words, bad_words)
        print("good_words:", list(good_words)[:5])
        print("bad_words:", list(bad_words)[:5])
        print("user_vector norm:", np.linalg.norm(user_vector))
        scored = []

        for i, emb in enumerate(self.embeddings):

            word = self._norm(self.index_to_word[i])

            # уже изученные не рекомендуем
            if word in good_words:
                continue

            sim = self._cosine(user_vector, emb)
            error_boost = self._error_boost(word, bad_words)

            # добавляем небольшую вариативность
            noise = np.random.normal(0, 0.01)

            score = sim + error_boost + noise
            scored.append((word, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [w for w, _ in scored[:top_n]]

    # =========================
    # USER VECTOR
    # =========================

    def _build_user_vector(self, good_words, bad_words):
        vectors = []

        for w in good_words:
            vec = self._get_vector(w)
            if vec is not None:
                vectors.append(vec)

        # ВАЖНО: не ноль-вектор
        if not vectors:
            return np.mean(self.embeddings, axis=0)

        vec = np.mean(vectors, axis=0)

        # нормализация
        norm = np.linalg.norm(vec)
        if norm != 0:
            vec = vec / norm

        return vec

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

        word = self._norm(word)
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

    def _filter_words(self, words):
        return {
            self._norm(w)
            for w in words
            if w and self._norm(w) in self.vocab
        }