import os

from pathlib import Path
from random import random

import numpy as np
import json


class WordRecommender:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent

        self.embeddings = np.load(base_dir / "embeddings.npy")

        with open(base_dir / "vocab.json", "r", encoding="utf-8") as f:
            raw_vocab = json.load(f)

        meta_path = base_dir / "word_meta.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                self.word_meta = json.load(f)
        else:
            self.word_meta = {}

        # нормализация vocab
        self.vocab = {
            k.strip().lower(): v
            for k, v in raw_vocab.items()
        }
        self.all_words = set(self.vocab.keys())
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

    def recommend(self, good_words, bad_words, top_n=10, excluded_words=None):

        good_words = {
            self._norm(w["word"])
            for w in good_words
        }

        bad_words = {
            self._norm(w["word"])
            for w in bad_words
        }

        excluded_words = {
            self._norm(w) for w in (excluded_words or set())
        }

        self.bad_words_raw = set(bad_words)

        if not good_words and not bad_words:
            return self._fallback_recommend(top_n)

        user_vector = self._build_user_vector(good_words, bad_words)
        print("good_words:", list(good_words)[:5])
        print("bad_words:", list(bad_words)[:5])
        print("user_vector norm:", np.linalg.norm(user_vector))
        scored = []

        for i, emb in enumerate(self.embeddings):

            word = self._norm(self.index_to_word[i])

            if word in good_words or word in bad_words or word in excluded_words:
                continue

            # и дополнительно исключаем bad words
            if word in self.bad_words_raw:
                continue

            sim = self._cosine(user_vector, emb)
            error_boost = self._error_boost(word, bad_words)

            score = sim + error_boost
            scored.append((word, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [w for w, _ in scored[:top_n]]

    def _fallback_recommend(self, top_n):
        # просто возвращаем случайные слова
        words = list(self.vocab.keys())
        random.shuffle(words)
        return words[:top_n]

    # =========================
    # USER VECTOR
    # =========================

    def _build_user_vector(self, good_words, bad_words):
        vectors = []

        for item in good_words:
            if isinstance(item, dict):
                w = item["word"]
            else:
                w = item

            vec = self._get_vector(w)
            if vec is not None:
                vectors.append(vec)

        # ВАЖНО: не ноль-вектор
        if not vectors:
            return np.mean(self.embeddings, axis=0) * 0.01

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
        word_vec = self._get_vector(word)
        if word_vec is None:
            return 0

        max_sim = 0

        for item in bad_words:
            if isinstance(item, dict):
                w = item["word"]
            else:
                w = item

            bad_vec = self._get_vector(w)
            if bad_vec is None:
                continue

            sim = self._cosine(word_vec, bad_vec)
            max_sim = max(max_sim, sim)

        # штрафуем похожие на "bad" слова
        return -max_sim * 0.3

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