class DictionaryService:
    def __init__(self, dict_repo, link_repo):
        self.dict_repo = dict_repo
        self.link_repo = link_repo

    def get_all_dictionaries(self):
        return self.dict_repo.get_all()

    def create_dictionary(self, name, description):
        self.dict_repo.create(name, description)

    def update_dictionary(self, dictionary_id, name, description):
        self.dict_repo.update(dictionary_id, name, description)

    def delete_dictionary(self, dictionary_id):
        self.dict_repo.delete(dictionary_id)

    def get_words(self, dictionary_id):
        return self.link_repo.get_words(dictionary_id)

    def add_word_to_dictionary(self, dictionary_id, word_id):
        self.link_repo.add_word_to_dictionary(dictionary_id, word_id)

    def remove_word_from_dictionary(self, dictionary_id, word_id):
        self.link_repo.remove_word_from_dictionary(dictionary_id, word_id)

    def get_by_id(self, dictionary_id):
        return self.dict_repo.get_by_id(dictionary_id)