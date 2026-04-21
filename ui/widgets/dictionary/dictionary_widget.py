from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
    QPushButton, QLabel, QFrame, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QHeaderView, QLineEdit, QSizePolicy
)

from ui.utils.constants import DIFFICULTY_MAP
from ui.widgets.dialogs.create_dictionary_dialog import CreateDictionaryDialog
from ui.widgets.dialogs.create_word_dialog import CreateWordDialog
from ui.widgets.dialogs.edit_word_dialog import EditWordDialog
import qtawesome as qta


class DictionaryWidget(QWidget):
    def __init__(self, service, main_window):
        super().__init__()

        self.service = service
        self.main_window = main_window

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # вкладки
        self.tabs = QTabWidget()

        self.dict_tab = QWidget()
        self.words_tab = QWidget()

        self.all_words = []
        self.filtered_words = []
        self.sort_column = -1
        self.sort_order = Qt.SortOrder.AscendingOrder

        self.dict_layout = QVBoxLayout()
        self.dict_tab.setLayout(self.dict_layout)

        self.words_layout = QVBoxLayout()
        self.words_tab.setLayout(self.words_layout)

        self.tabs.addTab(self.dict_tab, "Словари")
        self.tabs.addTab(self.words_tab, "Все слова")

        self.layout.addWidget(self.tabs)

        self.setup_dict_tab()
        self.setup_words_tab()

    def setup_dict_tab(self):
        self.clear_layout(self.dict_layout)

        # ===== BUTTON ADD =====
        btn_add = QPushButton("Добавить словарь")
        btn_add.clicked.connect(self.add_dictionary)
        self.dict_layout.addWidget(btn_add)

        # ===== SCROLL AREA SETUP =====
        from PyQt6.QtWidgets import QScrollArea, QWidget, QSizePolicy

        self.dict_container = QWidget()
        self.dict_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum
        )

        self.dict_inner_layout = QVBoxLayout(self.dict_container)
        self.dict_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.dict_inner_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.dict_container)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.dict_layout.addWidget(scroll)

        # ===== DATA =====
        dictionaries = self.service.get_all_dictionaries()

        if not dictionaries:
            self.dict_inner_layout.addWidget(QLabel("Словари отсутствуют"))
            return

        # ===== CARDS =====
        for d in dictionaries:
            card = QFrame()
            card.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Maximum
            )
            card.setStyleSheet("""
                QFrame {
                    border: 1px solid #333;
                    border-radius: 8px;
                    background-color: transparent;
                }
            """)

            layout = QVBoxLayout()
            layout.setContentsMargins(12, 10, 12, 10)
            layout.setSpacing(6)

            # ===== TOP ROW =====
            top_row = QHBoxLayout()

            btn = QPushButton(d["name"])
            btn.setStyleSheet("""
                text-align: left;
                background: transparent;
                border: none;
            """)
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )

            btn.clicked.connect(
                lambda _, id=d["id"]: self.main_window.open_dictionary(id)
            )

            delete_btn = QPushButton()
            delete_btn.setIcon(qta.icon('fa5s.trash', color=self.main_window.icon_color()))
            delete_btn.setFixedWidth(40)
            delete_btn.clicked.connect(
                lambda _, id=d["id"]: self.delete_dictionary_confirm(id)
            )

            top_row.addWidget(btn)
            top_row.addStretch()
            top_row.addWidget(delete_btn)

            # ===== DESCRIPTION =====
            info = QLabel(d["description"] or "")
            info.setWordWrap(True)
            info.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            info.setStyleSheet("opacity: 0.7;")

            # ===== BUILD CARD =====
            layout.addLayout(top_row)
            layout.addWidget(info)

            card.setLayout(layout)

            self.dict_inner_layout.addWidget(card)

        # ===== PUSH ITEMS UP =====
        self.dict_inner_layout.addStretch()

    def setup_words_tab(self):
        self.clear_layout(self.words_layout)

        # ================= SEARCH =================
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск слова")

        self.words_layout.addWidget(self.search_input)

        # ================= DATA =================
        self.all_words = self.main_window.word_service.get_all_words()
        self.filtered_words = self.all_words.copy()

        # ================= TABLE =================
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Оригинал", "Перевод", "Транскрипция", "Язык", "Сложность"
        ])

        self.words_layout.addWidget(self.table)

        # ================= EVENTS =================
        self.search_input.textChanged.connect(self.filter_words)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_words)
        self.table.cellDoubleClicked.connect(self.open_word_editor)

        # ================= BUTTON PANEL =================
        btn_container = QWidget()
        btn_container.setObjectName("buttonPanel")

        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)

        btn_add = QPushButton("Добавить слово")
        btn_add.clicked.connect(self.add_word_global)

        btn_delete = QPushButton("Удалить выбранные слова")
        btn_delete.clicked.connect(self.delete_selected_words)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()

        self.words_layout.addWidget(btn_container)

        # first render
        self.render_words()

    def render_words(self):
        self.table.setRowCount(len(self.filtered_words))

        for row, w in enumerate(self.filtered_words):
            self.table.setItem(row, 0, QTableWidgetItem(w["original"]))
            self.table.setItem(row, 1, QTableWidgetItem(w["translation"]))
            self.table.setItem(row, 2, QTableWidgetItem(w["transcription"] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(w["language"] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(
                DIFFICULTY_MAP.get(w["difficulty"], "")
            ))

            self.table.setVerticalHeaderItem(
                row,
                QTableWidgetItem(str(w["id"]))
            )

    def filter_words(self):
        text = self.search_input.text().lower().strip()

        if not text:
            self.filtered_words = self.all_words.copy()
        else:
            self.filtered_words = [
                w for w in self.all_words
                if text in w["original"].lower()
                   or text in w["translation"].lower()
            ]

        self.render_words()

    def sort_words(self, column):
        key_map = {
            0: "original",
            1: "translation",
            2: "transcription",
            3: "language",
            4: "difficulty",
        }

        key = key_map.get(column)
        if not key:
            return

        reverse = (
                self.sort_column == column and
                self.sort_order == Qt.SortOrder.AscendingOrder
        )

        def safe_value(w):
            value = w[key]
            return value if value is not None else ""

        self.filtered_words.sort(
            key=safe_value,
            reverse=reverse
        )

        self.sort_column = column
        self.sort_order = (
            Qt.SortOrder.DescendingOrder if reverse
            else Qt.SortOrder.AscendingOrder
        )

        self.render_words()

    def add_dictionary(self):
        dialog = CreateDictionaryDialog()

        if dialog.exec():
            data = dialog.get_data()

            if not data["name"]:
                return

            self.service.create_dictionary(
                data["name"],
                data["description"]
            )

            self.refresh()

    def delete_dictionary(self, dictionary_id):
        self.service.delete_dictionary(dictionary_id)
        self.refresh()

    def delete_dictionary_confirm(self, dictionary_id):
        reply = QMessageBox.question(
            self,
            "Удаление словаря",
            "Удалить словарь?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_dictionary(dictionary_id)
            self.refresh()

    def add_word_global(self):
        dialog = CreateWordDialog()

        if dialog.exec():
            data = dialog.get_data()

            self.main_window.word_service.create_word(data)
            self.refresh()

    def delete_word(self, word_id):
        reply = QMessageBox.question(
            self,
            "Удаление слова",
            "Удалить слово?\n\nОно будет удалено из списка слов и из всех словарей.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.word_service.delete_word(word_id)
            self.refresh()

    def delete_selected_words(self):
        rows = set(i.row() for i in self.table.selectedIndexes())

        if not rows:
            return

        reply = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранные слова?\nОни исчезнут из всех словарей.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        for row in rows:
            word_id = int(self.table.verticalHeaderItem(row).text())
            self.main_window.word_service.delete_word(word_id)

        self.refresh()

    def open_word_editor(self, row, column):
        word_id = int(self.table.verticalHeaderItem(row).text())

        word = self.main_window.word_service.get_word_by_id(word_id)

        dialog = EditWordDialog(word)

        if dialog.exec():
            data = dialog.get_data()

            self.main_window.word_service.update_word(word_id, data)

            #  ВАЖНО
            self.main_window.refresh_all()

    def refresh(self):
        self.setup_dict_tab()
        self.setup_words_tab()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

