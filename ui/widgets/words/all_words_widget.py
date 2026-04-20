from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QHBoxLayout
)


class AllWordsWidget(QWidget):
    def __init__(self, word_service):
        super().__init__()

        self.word_service = word_service

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_words()

    def load_words(self):
        words = self.word_service.get_all_words()

        if not words:
            self.layout.addWidget(QLabel("Нет слов"))
            return

        for w in words:
            row = QHBoxLayout()

            text = QLabel(
                f"{w['original']} - {w['translation']} "
                f"({w['language']}, {w['difficulty']})"
            )

            row.addWidget(text)

            container = QWidget()
            container.setLayout(row)

            self.layout.addWidget(container)