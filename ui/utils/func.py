from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView

from ui.utils.constants import DIFFICULTY_MAP


def create_words_table(words, selectable=False):
    table = QTableWidget()

    # ================= BASE STYLE =================
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.verticalHeader().setVisible(False)

    # ================= SELECTION =================
    if selectable:
        table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
    else:
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    # ================= HEADER STYLE =================
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    header.setStretchLastSection(True)

    # ================= COLUMNS =================
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels([
        "Оригинал", "Перевод", "Транскрипция", "Язык", "Сложность"
    ])

    table.setRowCount(len(words))

    for row, w in enumerate(words):
        table.setItem(row, 0, QTableWidgetItem(w["original"]))
        table.setItem(row, 1, QTableWidgetItem(w["translation"]))
        table.setItem(row, 2, QTableWidgetItem(w["transcription"] or ""))
        table.setItem(row, 3, QTableWidgetItem(w["language"] or ""))
        table.setItem(row, 4, QTableWidgetItem(
            DIFFICULTY_MAP.get(w["difficulty"], "Неизвестно")
        ))

        table.setVerticalHeaderItem(row, QTableWidgetItem(str(w["id"])))

    return table