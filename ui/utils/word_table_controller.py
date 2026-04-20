from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem


class WordTableController:
    def __init__(self, table, data, refresh_callback):
        self.table = table
        self.all_words = data
        self.filtered_words = data.copy()
        self.refresh_callback = refresh_callback

        self.sort_column = -1
        self.sort_order = Qt.SortOrder.AscendingOrder

    # ================= SEARCH =================
    def filter(self, text: str):
        text = text.lower().strip()

        if not text:
            self.filtered_words = self.all_words.copy()
        else:
            self.filtered_words = [
                w for w in self.all_words
                if text in w["original"].lower()
                or text in w["translation"].lower()
            ]

        self.refresh_callback(self.filtered_words)

    # ================= SORT =================
    def sort(self, column: int):
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

        self.filtered_words.sort(
            key=lambda w: w.get(key) or "",
            reverse=reverse
        )

        self.sort_column = column
        self.sort_order = (
            Qt.SortOrder.DescendingOrder if reverse
            else Qt.SortOrder.AscendingOrder
        )

        self.refresh_callback(self.filtered_words)