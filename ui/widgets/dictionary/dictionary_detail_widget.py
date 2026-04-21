from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QCheckBox, QTableWidgetItem, QAbstractItemView, QTableWidget, QMessageBox, QHeaderView,
    QFrame, QLineEdit
)

from ui.utils.constants import DIFFICULTY_MAP
from ui.widgets.dialogs.add_word_to_directory_dialog import AddWordToDictionaryDialog
from ui.widgets.dialogs.create_word_dialog import CreateWordDialog
import qtawesome as qta


class DictionaryDetailWidget(QWidget):
    def __init__(self, dict_service, word_service, dictionary_id, main_window):
        super().__init__()

        self.all_words = []
        self.filtered_words = []
        self.sort_column = -1
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.search_input = None
        self.table = None

        self.dict_service = dict_service
        self.word_service = word_service
        self.dictionary_id = dictionary_id
        self.main_window = main_window

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.checkboxes = []

        self.load_dictionary_info()
        self.load_words()
        self.setup_buttons()

    # ИНФОРМАЦИЯ О СЛОВАРЕ
    def load_dictionary_info(self):
        self.dictionary = self.dict_service.get_by_id(self.dictionary_id)

        self.info_box = QFrame()
        self.info_layout = QVBoxLayout()
        self.info_box.setLayout(self.info_layout)

        # ---------- НАЗВАНИЕ ----------
        self.name_row = QHBoxLayout()

        self.name_label = QLabel(self.dictionary["name"])
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.name_edit = QLineEdit(self.dictionary["name"])
        self.name_edit.hide()

        self.name_title = QLabel("Название:")
        self.name_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.name_title.setMinimumWidth(100)

        self.name_row.addWidget(self.name_title)
        self.name_row.addWidget(self.name_label)
        self.name_row.addWidget(self.name_edit)
        self.name_row.addStretch()  # ← ВАЖНО

        # ---------- КНОПКИ ----------
        self.edit_btn = QPushButton()
        self.save_btn = QPushButton()
        self.save_btn.hide()
        self.cancel_btn = QPushButton()
        self.cancel_btn.hide()

        self.edit_btn.clicked.connect(self.enable_edit)
        self.save_btn.clicked.connect(self.save_edit)
        self.cancel_btn.clicked.connect(self.cancel_edit)

        self.name_row.addStretch()
        self.name_row.addWidget(self.edit_btn)
        self.name_row.addWidget(self.save_btn)
        self.name_row.addWidget(self.cancel_btn)

        # ---------- ОПИСАНИЕ ----------
        self.desc_row = QHBoxLayout()

        self.desc_title = QLabel("Описание:")
        self.desc_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.desc_title.setMinimumWidth(100)

        self.desc_label = QLabel(self.dictionary["description"])
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.desc_edit = QLineEdit(self.dictionary["description"])
        self.desc_edit.hide()

        self.desc_row.addWidget(self.desc_title)
        self.desc_row.addWidget(self.desc_label)
        self.desc_row.addWidget(self.desc_edit)
        self.desc_row.addStretch()  # ← ВАЖНО

        # ---------- ДАТА ----------
        self.date_row = QHBoxLayout()

        self.date_title = QLabel("Дата:")
        self.date_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.date_title.setMinimumWidth(100)

        self.date_label = QLabel(self.dictionary["created_at"])
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.date_row.addWidget(self.date_title)
        self.date_row.addWidget(self.date_label)
        self.date_row.addStretch()

        # ---------- ДОБАВЛЕНИЕ ----------
        self.info_layout.addLayout(self.name_row)
        self.info_layout.addLayout(self.desc_row)
        self.info_layout.addLayout(self.date_row)

        self.layout.addWidget(self.info_box)

        self.edit_mode = False

    def toggle_edit_mode(self):
        if not self.edit_mode:
            self.enable_edit()
        else:
            self.save_edit()

    def enable_edit(self):
        self.edit_mode = True

        # текст → скрыть
        self.name_label.hide()
        self.desc_label.hide()

        # поля → показать
        self.name_edit.show()
        self.desc_edit.show()

        # кнопки
        self.edit_btn.hide()
        self.save_btn.show()
        self.cancel_btn.show()

    def cancel_edit(self):
        self.edit_mode = False

        # вернуть старые значения
        self.name_edit.setText(self.dictionary["name"])
        self.desc_edit.setText(self.dictionary["description"])

        # переключение обратно
        self.name_edit.hide()
        self.desc_edit.hide()

        self.name_label.show()
        self.desc_label.show()

        self.save_btn.hide()
        self.cancel_btn.hide()
        self.edit_btn.show()

    def save_edit(self):
        self.edit_mode = False

        new_name = self.name_edit.text()
        new_desc = self.desc_edit.text()

        self.dict_service.update_dictionary(
            self.dictionary_id,
            new_name,
            new_desc
        )

        self.main_window.training_view.reload_dictionaries()

        # обновляем локально

        self.name_label.setText(new_name)
        self.desc_label.setText(new_desc)

        # переключение обратно
        self.name_edit.hide()
        self.desc_edit.hide()

        self.name_label.show()
        self.desc_label.show()

        self.save_btn.hide()
        self.cancel_btn.hide()
        self.edit_btn.show()

    def clear_info_layout(self):
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_words(self):
        self.clear_words_area()

        words = self.dict_service.get_words(self.dictionary_id)

        self.all_words = words
        self.filtered_words = words.copy()

        # ================= SEARCH =================
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по словам в словаре")
        self.search_input.textChanged.connect(self.filter_words)

        self.layout.addWidget(self.search_input)

        # ================= TABLE =================
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.sectionClicked.connect(self.sort_words)

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Оригинал", "Перевод", "Транскрипция", "Язык", "Сложность"
        ])

        self.table.cellDoubleClicked.connect(self.open_word_editor)

        self.layout.addWidget(self.table)

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
                if text in (w["original"] or "").lower()
                   or text in (w["translation"] or "").lower()
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

        def safe(w):
            return w[key] if w[key] is not None else ""

        self.filtered_words.sort(key=safe, reverse=reverse)

        self.sort_column = column
        self.sort_order = (
            Qt.SortOrder.DescendingOrder if reverse
            else Qt.SortOrder.AscendingOrder
        )

        self.render_words()

    def clear_words_area(self):
        if self.search_input:
            self.search_input.deleteLater()
            self.search_input = None

        if self.table:
            self.table.deleteLater()
            self.table = None

    def open_word_editor(self, row, column):
        word_id = int(self.table.verticalHeaderItem(row).text())

        word = self.word_service.get_word_by_id(word_id)

        from ui.widgets.dialogs.edit_word_dialog import EditWordDialog
        dialog = EditWordDialog(word)

        if dialog.exec():
            data = dialog.get_data()

            self.word_service.update_word(word_id, data)

            # ОБНОВЛЯЕМ ВСЁ
            self.main_window.refresh_all()

    # КНОПКИ
    def setup_buttons(self):
        # ================= BUTTON PANEL =================
        btn_container = QWidget()
        btn_container.setObjectName("buttonPanel")

        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)

        btn_add = QPushButton("Добавить слово")
        btn_add.clicked.connect(self.add_word)

        btn_delete = QPushButton("Удалить выбранные")
        btn_delete.clicked.connect(self.delete_selected)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()

        self.layout.addWidget(btn_container)

    # ➕ добавить слово
    def add_word(self):

        # получаем уже существующие слова в словаре
        words = self.dict_service.get_words(self.dictionary_id)
        existing_ids = [w["id"] for w in words]

        dialog = AddWordToDictionaryDialog(self.word_service, existing_ids)

        if dialog.exec():
            result = dialog.get_result()

            if result["mode"] == "new":
                word_id = self.word_service.create_word(result["data"])
                self.dict_service.add_word_to_dictionary(self.dictionary_id, word_id)

            elif result["mode"] == "existing":
                for word_id in result["word_ids"]:
                    self.dict_service.add_word_to_dictionary(self.dictionary_id, word_id)

            self.main_window.refresh_all()

    # удалить выбранные
    def delete_selected(self):
        rows = set(i.row() for i in self.table.selectedIndexes())

        if not rows:
            return

        reply = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранные слова из словаря?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        for row in rows:
            word_id = int(self.table.verticalHeaderItem(row).text())
            self.dict_service.remove_word_from_dictionary(self.dictionary_id, word_id)

        self.refresh()

    def refresh(self):

        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.checkboxes = []

        self.load_dictionary_info()
        self.load_words()
        self.setup_buttons()

    def update_icons(self, theme: str):
        if theme == "dark":
            color = "#BBBBBB"
        else:
            color = "#444444"

        self.edit_btn.setIcon(qta.icon('fa5s.edit', color=color))
        self.save_btn.setIcon(qta.icon('fa5s.check', color=color))
        self.cancel_btn.setIcon(qta.icon('fa5s.times', color=color))