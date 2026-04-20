class WordService:
    def __init__(self, word_repo, link_repo):
        self.word_repo = word_repo
        self.link_repo = link_repo

    def get_all_words(self):
        return self.word_repo.get_all()

    def create_word(self, data):
        return self.word_repo.create(data)

    def get_last_word(self):
        return self.word_repo.get_last()

    def delete_word(self, word_id):
        # 1. удалить связи со словарями
        self.link_repo.remove_word_everywhere(word_id)
        # 2. удалить само слово
        self.word_repo.delete(word_id)

    def get_word_by_id(self, word_id):
        return self.word_repo.get_by_id(word_id)

    def update_word(self, word_id, data):
        self.word_repo.update(word_id, data)
