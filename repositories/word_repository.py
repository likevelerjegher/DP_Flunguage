class WordRepository:
    def __init__(self, storage):
        self.storage = storage

    def get_all(self):
        return self.storage.fetch_all("SELECT * FROM words")

    def create(self, word):
        cursor = self.storage.conn.cursor()

        cursor.execute(
            """INSERT INTO words 
            (original, translation, transcription, language, difficulty)
            VALUES (?, ?, ?, ?, ?)""",
            (
                word["original"],
                word["translation"],
                word["transcription"],
                word["language"],
                word["difficulty"]
            )
        )

        self.storage.conn.commit()
        return cursor.lastrowid

    def get_last(self):
        return self.storage.fetch_one(
            "SELECT * FROM words ORDER BY id DESC LIMIT 1"
        )

    def get_by_id(self, word_id):
        return self.storage.fetch_one(
            "SELECT * FROM words WHERE id = ?", (word_id,)
        )

    def update(self, word_id, data):
        self.storage.execute("""
            UPDATE words
            SET original = ?,
                translation = ?,
                transcription = ?,
                language = ?,
                difficulty = ?
            WHERE id = ?
        """, (
            data["original"],
            data["translation"],
            data["transcription"],
            data["language"],
            data["difficulty"],
            word_id
        ))

    def delete(self, word_id):
        # сначала удаляем связи со словарями
        self.storage.execute(
            "DELETE FROM dictionary_words WHERE word_id = ?",
            (word_id,)
        )

        # потом само слово
        self.storage.execute(
            "DELETE FROM words WHERE id = ?",
            (word_id,)
        )
