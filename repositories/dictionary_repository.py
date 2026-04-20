class DictionaryRepository:
    def __init__(self, storage):
        self.storage = storage

    def get_all(self):
        return self.storage.fetch_all("SELECT * FROM dictionaries")

    def create(self, name, description):
        self.storage.execute(
            "INSERT INTO dictionaries (name, description, created_at) VALUES (?, ?, datetime('now'))",
            (name, description)
        )

    def update(self, dictionary_id, name, description):
        self.storage.execute("""
            UPDATE dictionaries
            SET name = ?,
                description = ?
            WHERE id = ?
        """, (name, description, dictionary_id))

    def delete(self, dictionary_id):
        self.storage.execute(
            "DELETE FROM dictionaries WHERE id = ?",
            (dictionary_id,)
        )

    def get_by_id(self, dictionary_id):
        return self.storage.fetch_one(
            "SELECT * FROM dictionaries WHERE id = ?",
            (dictionary_id,)
        )