import json


def load_words(path="ml/words.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_vocab(words):
    vocab = {w["word"]: i for i, w in enumerate(words)}
    return vocab


def words_to_indices(words, vocab):
    return [vocab[w["word"]] for w in words]