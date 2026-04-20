class DictionaryWordRepository:
    def __init__(self, storage):
        self.storage = storage

    def add_word_to_dictionary(self, dictionary_id, word_id):
        self.storage.execute(
            "INSERT OR IGNORE INTO dictionary_words (dictionary_id, word_id) VALUES (?, ?)",
            (dictionary_id, word_id)
        )

    def remove_word_from_dictionary(self, dictionary_id, word_id):
        self.storage.execute(
            "DELETE FROM dictionary_words WHERE dictionary_id = ? AND word_id = ?",
            (dictionary_id, word_id)
        )

    def get_words(self, dictionary_id):
        return self.storage.fetch_all("""
            SELECT w.*
            FROM words w
            JOIN dictionary_words dw ON w.id = dw.word_id
            WHERE dw.dictionary_id = ?
        """, (dictionary_id,))

    def remove_word_everywhere(self, word_id):
        self.storage.execute(
            "DELETE FROM dictionary_words WHERE word_id = ?",
            (word_id,)
        )