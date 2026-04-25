import json
import numpy as np
from model import build_model
import re
import random


# =========================
# LOAD DATA
# =========================
def load_words(path="dataset_words.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# VOCAB
# =========================
def build_vocab(words):
    return {w["word"]: i for i, w in enumerate(words)}


# =========================
# TOKENIZER
# =========================
def tokenize(text):
    return re.findall(r"[a-z]+", text.lower())


# =========================
# BUILD PAIRS (FAST VERSION)
# =========================
def build_pairs(words, vocab):

    pairs = []

    # POS index
    pos_index = {}
    for w in words:
        pos_index.setdefault(w["pos"], []).append(w["word"])

    # FIX: build translation index ONCE
    translation_to_words = {}
    for item in words:
        for tr in item.get("translations", []):
            tr = tr.strip().lower()
            translation_to_words.setdefault(tr, []).append(item["word"])

    for i, w in enumerate(words):

        target = w["word"]

        # =========================
        # 1. definition signal
        # =========================
        tokens = tokenize(w["definition"])[:5]

        for t in tokens:
            if t in vocab and t != target:
                pairs.append((target, t, 2.0))

        # =========================
        # 2. POS signal
        # =========================
        same_pos_words = pos_index.get(w["pos"], [])

        sampled = random.sample(
            same_pos_words,
            min(3, len(same_pos_words))
        )

        for other in sampled:
            if other != target:
                pairs.append((target, other, 0.5))

        # =========================
        # 3. translation signal (FAST)
        # =========================
        for tr in w.get("translations", [])[:3]:
            tr = tr.strip().lower()

            for other_word in translation_to_words.get(tr, [])[:5]:
                if other_word != target:
                    pairs.append((target, other_word, 3.0))
                    break

        # =========================
        # progress log
        # =========================
        if i % 1000 == 0:
            print(f"processed words: {i}/{len(words)} | pairs: {len(pairs)}")

    # remove duplicates
    pairs = list(dict.fromkeys(pairs))

    return pairs


# =========================
# NEGATIVE SAMPLING DATASET
# =========================
def build_training_data(pairs, vocab, num_negative=1):

    X_target, X_context, y, weights = [], [], [], []

    vocab_words = list(vocab.keys())

    positive_set = set()
    for t, c, _ in pairs:
        positive_set.add(t)
        positive_set.add(c)

    for i, (t, c, w) in enumerate(pairs):

        X_target.append(vocab[t])
        X_context.append(vocab[c])
        y.append(1)
        weights.append(w)

        for _ in range(num_negative):
            neg = random.choice(vocab_words)
            while neg in positive_set:
                neg = random.choice(vocab_words)

            X_target.append(vocab[t])
            X_context.append(vocab[neg])
            y.append(0)
            weights.append(1.0)

        if i % 5000 == 0:
            print(f"built samples: {i}/{len(pairs)}")

    return (
        np.array(X_target),
        np.array(X_context),
        np.array(y),
        np.array(weights),
    )


# =========================
# TRAIN
# =========================
def train():

    words = load_words()
    vocab = build_vocab(words)

    print("building pairs...")
    pairs = build_pairs(words, vocab)
    print("pairs:", len(pairs))

    random.shuffle(pairs)
    pairs = pairs[:50000]

    print("building training data...")
    X_target, X_context, y, w = build_training_data(
        pairs,
        vocab,
        num_negative=1
    )

    print("training samples:", len(X_target))

    print("building model...")
    model = build_model(len(vocab))

    print("training started...")
    model.fit(
        [X_target, X_context],
        y,
        sample_weight=w,
        epochs=5,
        batch_size=256,
        verbose=1
    )

    embeddings = model.get_layer("emb").get_weights()[0]

    np.save("embeddings.npy", embeddings)

    with open("vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False)

    word_meta = {
        w["word"].strip().lower(): {
            "word": w["word"].strip().lower(),
            "translations": w.get("translations", []),
            "pos": w.get("pos", "")
        }
        for w in words
    }

    with open("word_meta.json", "w", encoding="utf-8") as f:
        json.dump(word_meta, f, ensure_ascii=False, indent=2)

    print("done")


if __name__ == "__main__":
    train()