from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt


class StatWidget(QWidget):
    def __init__(self, training_repo):
        super().__init__()

        self.training_repo = training_repo

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ===== TITLE =====
        title = QLabel("Статистика")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.layout.addWidget(title)

        # ===== GENERAL STATS =====
        self.general_label = QLabel()
        self.layout.addWidget(self.general_label)

        # ===== DELETE BUTTON =====
        self.delete_session_btn = QPushButton("Удалить сессию")
        self.delete_session_btn.clicked.connect(self.delete_selected_sessions)

        self.layout.addWidget(self.delete_session_btn)

        # ===== LAST SESSIONS =====
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(4)
        self.sessions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sessions_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.sessions_table.setHorizontalHeaderLabels([
            "Дата", "Слов", "%", "Время (сек)"
        ])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(QLabel("Последние тренировки"))
        self.layout.addWidget(self.sessions_table)

        # ===== HARD WORDS =====
        self.words_table = QTableWidget()
        self.words_table.setColumnCount(3)
        self.words_table.setHorizontalHeaderLabels([
            "Слово", "Ошибки", "Успех %"
        ])
        self.words_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(QLabel("Сложные слова"))
        self.layout.addWidget(self.words_table)

        self.load_stats()

    # ================= LOAD DATA =================

    def load_stats(self):
        self.load_general_stats()
        self.load_sessions()
        self.load_hard_words()

    # ================= GENERAL =================

    def load_general_stats(self):
        stats = self.training_repo.get_general_stats()

        self.general_label.setText(
            f"Всего ответов: {stats['total']}\n"
            f"Точность: {stats['accuracy']}%\n"
            f"Среднее время: {stats['avg_time']} сек"
        )

    # ================= SESSIONS =================

    def load_sessions(self):
        rows = self.training_repo.get_last_sessions()

        self.sessions_table.setRowCount(len(rows))

        for i, (session_id, date, words_count, score, duration) in enumerate(rows):
            self.sessions_table.setItem(i, 0, QTableWidgetItem(date[:19]))
            self.sessions_table.setItem(i, 1, QTableWidgetItem(str(words_count)))
            self.sessions_table.setItem(i, 2, QTableWidgetItem(f"{score}%"))
            self.sessions_table.setItem(i, 3, QTableWidgetItem(str(duration)))

            # сохраняем id в строке
            self.sessions_table.setRowHeight(i, 20)
            self.sessions_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, session_id)

    # ================= HARD WORDS =================

    def load_hard_words(self):
        rows = self.training_repo.get_hard_words()

        self.words_table.setRowCount(len(rows))

        for i, (word, wrong, success) in enumerate(rows):
            self.words_table.setItem(i, 0, QTableWidgetItem(word))
            self.words_table.setItem(i, 1, QTableWidgetItem(str(wrong)))
            self.words_table.setItem(i, 2, QTableWidgetItem(f"{int(success)}%"))

    def delete_session(self, session_id):
        self.training_repo.delete_session(session_id)

        self.refresh_stats()

    def refresh_stats(self):
        self.load_stats()

    def delete_selected_sessions(self):
        selected_rows = self.sessions_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        reply = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранные сессии?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        session_ids = []

        for index in selected_rows:
            session_id = self.sessions_table.item(index.row(), 0).data(Qt.ItemDataRole.UserRole)
            session_ids.append(session_id)

        for session_id in session_ids:
            self.training_repo.delete_session(session_id)

        self.refresh_stats()

