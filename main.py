import sys
from PyQt6.QtWidgets import QApplication
from database.init_db import init_db
from repositories.dictionary_repository import DictionaryRepository
from repositories.dictionary_word_repository import DictionaryWordRepository
from repositories.word_repository import WordRepository
from services.data_storage_service import DataStorageService
from services.dictionary_service import DictionaryService
from services.word_service import WordService
from ui.main_window import MainWindow


def main():
    init_db()

    app = QApplication(sys.argv)

    storage = DataStorageService("app.db")
    word_repo = WordRepository(storage)
    dict_repo = DictionaryRepository(storage)
    link_repo = DictionaryWordRepository(storage)

    word_service = WordService(word_repo, link_repo)
    dictionary_service = DictionaryService(dict_repo, link_repo)

    window = MainWindow(dictionary_service, word_service)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()