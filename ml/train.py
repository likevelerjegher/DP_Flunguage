import json
import numpy as np
from model import build_model
import re
import random


def load_words(path="dataset_words.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_vocab(words):
    return {w["word"]: i for i, w in enumerate(words)}


def tokenize(text):
    text = text.lower()
    words = re.findall(r"[a-z]+", text)
    return words


def word_to_index(words, vocab):
    return np.array([vocab[w["word"]] for w in words])


def build_pairs(words, vocab):
    pairs = []

    # индекс по частям речи
    pos_index = {}
    for w in words:
        pos_index.setdefault(w["pos"], []).append(w["word"])

    for w in words:
        target = w["word"]

        # =========================
        # 1. definition pairs (сильный сигнал)
        # =========================
        tokens = tokenize(w["definition"])[:5]

        for t in tokens:
            if t in vocab and t != target:
                pairs.append((target, t, 2.0))  # вес 2.0

        # =========================
        # 2. same POS pairs (слабее)
        # =========================
        same_pos_words = pos_index.get(w["pos"], [])

        # случайно выбираем, а не первые 5
        sampled = random.sample(
            same_pos_words,
            min(5, len(same_pos_words))
        )

        for other in sampled:
            if other != target:
                pairs.append((target, other, 0.5))  # вес 0.5

    return pairs


def build_training_data(pairs, vocab, num_negative=1):
    X_target = []
    X_context = []
    y = []
    sample_weight = []

    vocab_words = list(vocab.keys())

    # ОДИН РАЗ
    positive_set = set([c for _, c, _ in pairs])

    for t, c, weight in pairs:
        # положительный пример
        X_target.append(vocab[t])
        X_context.append(vocab[c])
        y.append(1)
        sample_weight.append(weight)

        # отрицательные
        for _ in range(num_negative):
            neg = get_negative(vocab_words, positive_set)

            X_target.append(vocab[t])
            X_context.append(vocab[neg])
            y.append(0)
            sample_weight.append(1.0)

    return np.array(X_target), np.array(X_context), np.array(y), np.array(sample_weight)

def get_negative(vocab_words, positive_set):
    while True:
        neg = random.choice(vocab_words)
        if neg not in positive_set:
            return neg


def pairs_to_arrays(pairs, vocab):
    X_target = []
    X_context = []

    for t, c in pairs:
        X_target.append(vocab[t])
        X_context.append(vocab[c])

    return np.array(X_target), np.array(X_context)


def train():
    words = load_words()
    vocab = build_vocab(words)

    pairs = build_pairs(words, vocab)
    print("pairs:", len(pairs))
    random.shuffle(pairs)
    pairs = pairs[:150000]
    X_target, X_context, y, w = build_training_data(pairs, vocab, num_negative=2)
    print("training data ready:", len(X_target))
    model = build_model(len(vocab))

    model.fit(
        [X_target, X_context],
        y,
        sample_weight=w,
        epochs=7,
        batch_size=64
    )

    embeddings = model.get_layer("emb").get_weights()[0]

    np.save("embeddings.npy", embeddings)

    with open("vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False)


if __name__ == "__main__":
    train()