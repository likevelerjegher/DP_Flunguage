from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit,
    QPushButton, QComboBox
)

from ui.utils.constants import LANGUAGES, DIFFICULTY_LEVELS


class CreateWordDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Добавить слово")

        layout = QVBoxLayout()

        self.original = QLineEdit()
        self.original.setPlaceholderText("Слово")

        self.translation = QLineEdit()
        self.translation.setPlaceholderText("Перевод")

        self.transcription = QLineEdit()
        self.transcription.setPlaceholderText("Транскрипция")

        # язык
        self.language = QComboBox()
        self.language.addItems(LANGUAGES)

        # сложность
        self.difficulty = QComboBox()
        self.difficulty.addItems(DIFFICULTY_LEVELS)

        self.btn_create = QPushButton("Добавить")

        layout.addWidget(self.original)
        layout.addWidget(self.translation)
        layout.addWidget(self.transcription)
        layout.addWidget(self.language)
        layout.addWidget(self.difficulty)
        layout.addWidget(self.btn_create)

        self.setLayout(layout)

        self.btn_create.clicked.connect(self.accept)

    def get_data(self):
        return {
            "original": self.original.text(),
            "translation": self.translation.text(),
            "transcription": self.transcription.text(),
            "language": self.language.currentText(),
            "difficulty": self.difficulty.currentIndex() + 1
        }