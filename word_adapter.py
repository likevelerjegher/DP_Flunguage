# ml/word_adapter.py

def normalize_word(w):
    if w is None:
        return None

    # sqlite3.Row / dict / object → dict
    w = dict(w)

    word = w.get("word") or w.get("original") or w.get("bare")
    if not word:
        return None

    return {
        "word": word,
        "translation": _normalize_translation(w),
        "pos": w.get("pos", "unknown"),
        "difficulty": w.get("difficulty", 0.5),
        "correct_count": w.get("correct_count", 0),
        "wrong_count": w.get("wrong_count", 0)
    }


def _normalize_translation(w):
    t = w.get("translation")

    if isinstance(t, list):
        return t

    if isinstance(t, str):
        return [x.strip() for x in t.split(",") if x.strip()]

    return []