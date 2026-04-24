import re
import json
import csv


# =========================
# CLEAN DEFINITION
# =========================
def clean_definition(text: str) -> str:
    # убираем [latin], [greek] и любые [..]
    text = re.sub(r"\[[^\]]*\]", "", text)

    # убираем лишние пробелы
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =========================
# NORMALIZE TRANSLATIONS
# =========================
def normalize_translations(trans_list):
    cleaned = set()

    for t in trans_list:
        t = t.strip().lower()

        # убираем пустые
        if not t:
            continue

        # убираем лишние пробелы внутри
        t = re.sub(r"\s+", " ", t)

        cleaned.add(t)

    return list(cleaned)


# =========================
# PARSE TXT
# =========================
def parse_txt_dictionary(path):
    data = {}

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(r"^([A-Za-z\-]+)\s+(.*)", line)
        if not match:
            continue

        word = match.group(1).lower()
        rest = match.group(2)

        pos_match = re.search(r"\b(n|v|adj|adv|prep|prefix|abbr)\.", rest)
        pos = pos_match.group(1) if pos_match else "other"

        definition = clean_definition(rest)

        data[word] = {
            "pos": pos,
            "definition": definition
        }

    return data


# =========================
# PARSE CSV
# =========================
def normalize_key(key):
    return key.strip().lower().replace("\ufeff", "")


def parse_csv_files(paths):
    result = {}

    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            field_map = {normalize_key(k): k for k in reader.fieldnames}

            bare_key = field_map.get("bare")
            trans_key = field_map.get("translations_en")

            if not bare_key or not trans_key:
                continue

            for row in reader:
                ru = row[bare_key].strip()
                en_words = row[trans_key]

                if not en_words:
                    continue

                for w in re.split(r"[;,]", en_words):
                    word = w.strip().lower()

                    if not word:
                        continue

                    result.setdefault(word, []).append(ru)

    return result


# =========================
# MERGE + DEDUP
# =========================
def merge_data(txt_data, csv_data):
    final = {}

    for word, ru_list in csv_data.items():

        if word not in txt_data:
            continue

        info = txt_data[word]

        if word not in final:
            final[word] = {
                "word": word,
                "pos": info["pos"],
                "definition": clean_definition(info["definition"]),
                "translations": set()
            }

        for ru in ru_list:
            ru = ru.strip().lower()
            if ru:
                final[word]["translations"].add(ru)

    # set → list
    for word in final:
        final[word]["translations"] = sorted(list(final[word]["translations"]))

    return list(final.values())


# =========================
# MAIN
# =========================
def main():
    txt_path = "dictionaries_stock/dictionary_eng.txt"

    csv_paths = [
        "dictionaries_stock/nouns.csv",
        "dictionaries_stock/verbs.csv",
        "dictionaries_stock/adjectives.csv",
        "dictionaries_stock/others.csv"
    ]

    print("Parsing TXT...")
    txt_data = parse_txt_dictionary(txt_path)

    print("Parsing CSV...")
    csv_data = parse_csv_files(csv_paths)

    print("Merging...")
    final_data = merge_data(txt_data, csv_data)

    print("Total words:", len(final_data))

    with open("dataset_words.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print("Saved: dataset_words.json")


if __name__ == "__main__":
    main()