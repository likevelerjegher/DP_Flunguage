from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QRadioButton, QButtonGroup,
    QWidget, QStackedWidget, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHBoxLayout, QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt

from ui.utils.constants import DIFFICULTY_MAP, LANGUAGES, DIFFICULTY_LEVELS
from ui.utils.func import create_words_table


class AddWordToDictionaryDialog(QDialog):
    def __init__(self, word_service, dictionary_word_ids):
        super().__init__()

        self.word_service = word_service
        self.dictionary_word_ids = set(dictionary_word_ids)

        self.setWindowTitle("Добавить слово в словарь")
        self.resize(750, 550)

        # ================= ROOT =================
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        # ================= MODE =================
        self.radio_new = QRadioButton("Создать новое слово")
        self.radio_existing = QRadioButton("Выбрать существующее")
        self.radio_new.setChecked(True)

        self.group = QButtonGroup()
        self.group.addButton(self.radio_new)
        self.group.addButton(self.radio_existing)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.radio_new)
        mode_layout.addWidget(self.radio_existing)
        mode_layout.addStretch()

        layout.addLayout(mode_layout)

        # ================= STACK =================
        self.stack = QStackedWidget()

        # =====================================================
        # 🔹 PAGE 1: NEW WORD
        # =====================================================
        self.page_new = QWidget()
        new_layout = QVBoxLayout()
        new_layout.setContentsMargins(20, 10, 20, 10)
        new_layout.setSpacing(10)

        form = QVBoxLayout()
        form.setSpacing(8)

        def make_input(placeholder):
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setMinimumHeight(32)
            return inp

        self.input_original = make_input("Оригинал")
        self.input_translation = make_input("Перевод")
        self.input_transcription = make_input("Транскрипция")

        self.combo_language = QComboBox()
        self.combo_language.addItems(LANGUAGES)
        self.combo_language.setMinimumHeight(32)

        self.combo_difficulty = QComboBox()
        self.combo_difficulty.addItems(DIFFICULTY_LEVELS)
        self.combo_difficulty.setMinimumHeight(32)

        form.addWidget(self.input_original)
        form.addWidget(self.input_translation)
        form.addWidget(self.input_transcription)
        form.addWidget(self.combo_language)
        form.addWidget(self.combo_difficulty)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addStretch()
        wrapper_layout.addLayout(form)
        wrapper_layout.addStretch()
        wrapper.setLayout(wrapper_layout)

        new_layout.addWidget(wrapper)
        self.page_new.setLayout(new_layout)

        # =====================================================
        # PAGE 2: EXISTING WORDS (FINAL)
        # =====================================================
        self.page_existing = QWidget()
        existing_layout = QVBoxLayout()

        # ================= SEARCH =================
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск слова")
        self.search_input.setMinimumHeight(32)

        existing_layout.addWidget(self.search_input)

        # ================= DATA =================
        words = self.word_service.get_all_words()

        self.all_words = [
            w for w in words
            if w["id"] not in self.dictionary_word_ids
        ]

        self.filtered_words = self.all_words.copy()

        # ================= EMPTY LABEL =================
        self.empty_label = QLabel("Отсутствуют уникальные слова для добавления")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ================= TABLE =================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Оригинал", "Перевод", "Транскрипция", "Язык", "Сложность"
        ])

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        existing_layout.addWidget(self.empty_label)
        existing_layout.addWidget(self.table)

        self.page_existing.setLayout(existing_layout)

        # ================= STACK ADD =================
        self.stack.addWidget(self.page_new)
        self.stack.addWidget(self.page_existing)

        layout.addWidget(self.stack)

        self.render_words()

        # ================= BUTTON =================
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Добавить")
        self.btn_add.setMinimumHeight(35)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_add)

        layout.addLayout(btn_layout)

        # ================= SIGNALS =================
        self.radio_new.toggled.connect(self.switch_mode)
        self.radio_existing.toggled.connect(self.switch_mode)

        self.btn_add.clicked.connect(self.accept)
        self.search_input.textChanged.connect(self.filter_words)

    # ================= MODE SWITCH =================
    def switch_mode(self):
        if self.radio_new.isChecked():
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)

    # ================= RESULT =================
    def get_result(self):
        if self.radio_new.isChecked():
            return {
                "mode": "new",
                "data": {
                    "original": self.input_original.text(),
                    "translation": self.input_translation.text(),
                    "transcription": self.input_transcription.text(),
                    "language": self.combo_language.currentText(),
                    "difficulty": self.combo_difficulty.currentIndex() + 1
                }
            }

        if not self.table:
            return {
                "mode": "existing",
                "word_ids": []
            }

        rows = set(i.row() for i in self.table.selectedIndexes())

        word_ids = [
            int(self.table.verticalHeaderItem(r).text())
            for r in rows
        ]

        return {
            "mode": "existing",
            "word_ids": word_ids
        }

    def filter_words(self):
        text = self.search_input.text().lower().strip()

        if not text:
            self.filtered_words = self.all_words.copy()
        else:
            self.filtered_words = [
                w for w in self.all_words
                if text in (w["original"] or "").lower()
                   or text in (w["translation"] or "").lower()
            ]

        self.render_words()

    def render_words(self):
        if not self.filtered_words:
            self.table.hide()
            self.empty_label.show()
            return

        self.empty_label.hide()
        self.table.show()

        self.table.setRowCount(len(self.filtered_words))

        for row, w in enumerate(self.filtered_words):
            self.table.setItem(row, 0, QTableWidgetItem(w["original"] or ""))
            self.table.setItem(row, 1, QTableWidgetItem(w["translation"] or ""))
            self.table.setItem(row, 2, QTableWidgetItem(w["transcription"] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(w["language"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(
                DIFFICULTY_MAP.get(w["difficulty"], "")
            ))

            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(w["id"])))
