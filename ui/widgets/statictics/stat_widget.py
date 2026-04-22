from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox, QHBoxLayout, QScrollArea, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.no_scroll_propagation_table import NoScrollPropagationTable
from ui.styles.button_styles import danger_button_style

MAX_TABLE_ROWS = 8
ROW_HEIGHT = 20
HEADER_HEIGHT = 25

class StatWidget(QWidget):
    def __init__(self, training_repo):
        super().__init__()

        self.training_repo = training_repo

        # ===== SCROLL AREA =====
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()

        self.layout = QVBoxLayout(self.container)

        self.scroll.setWidget(self.container)

        self.container.setMinimumWidth(600)
        self.container.setMinimumHeight(800)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll)

        # ===== TITLE =====
        title = QLabel("Статистика")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(title)
        self.layout.addSpacing(15)

        # ===== GENERAL =====
        self.general_label = QLabel()
        self.layout.addWidget(self.general_label)

        # ===== CHART =====
        label_hard = QLabel("Уровень усвоения слов")
        self.make_label_clean(label_hard)

        self.layout.addSpacing(15)
        self.layout.addWidget(label_hard)

        self.chart = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax = self.chart.figure.add_subplot(111)

        self.chart.setFixedHeight(190)
        self.chart.setMinimumWidth(600)

        self.chart.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        self.chart.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.chart.wheelEvent = lambda event: event.ignore()
        self.chart.setAttribute(Qt.WidgetAttribute.WA_NoMousePropagation, True)

        # без stretch
        self.layout.addWidget(self.chart)
        self.layout.addSpacing(15)

        # ===== WORDS TABLE =====
        self.words_table = NoScrollPropagationTable()
        self.words_table.setColumnCount(3)

        self.words_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        self.words_table.setHorizontalHeaderLabels([
            "Слово", "Ошибки", "Статус"
        ])
        self.words_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.words_table)

        # ===== SESSIONS TABLE =====
        label_sessions = QLabel("Последние тренировки")
        self.make_label_clean(label_sessions)

        self.layout.addSpacing(15)
        self.layout.addWidget(label_sessions)

        self.sessions_table = NoScrollPropagationTable()
        self.sessions_table.setColumnCount(5)
        self.sessions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sessions_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        self.sessions_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        self.sessions_table.setHorizontalHeaderLabels([
            "Дата", "Режим", "Кол-во слов", "%", "Время"
        ])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.sessions_table)

        # ===== BUTTON =====
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.delete_session_btn = QPushButton("Удалить тренировку")
        self.delete_session_btn.setStyleSheet(
            danger_button_style(self.is_dark_theme())
        )

        btn_row.addWidget(self.delete_session_btn)
        self.layout.addLayout(btn_row)

        self.load_stats()
        self.delete_session_btn.clicked.connect(self.delete_selected_sessions)
    # ================= LOAD DATA =================

    def load_stats(self):
        self.load_general_stats()
        self.load_sessions()
        self.load_chart()
        self.load_hard_words()

    # ================= GENERAL =================

    def load_general_stats(self):
        stats = self.training_repo.get_general_stats()
        words_count = self.training_repo.get_words_count()

        self.general_label.setText(
            f"Всего слов: {words_count}\n"
            f"Всего ответов: {stats['total']}\n"
            f"Точность: {stats['accuracy']}%\n"
            f"Среднее время: {stats['avg_time']} сек"
        )

    # ================= SESSIONS =================

    def load_sessions(self):
        rows = self.training_repo.get_last_sessions()

        self.sessions_table.setRowCount(len(rows))

        for i, (session_id, date, mode, words_count, score, duration) in enumerate(rows):
            self.sessions_table.setItem(i, 0, QTableWidgetItem(date[:19]))
            self.sessions_table.setItem(i, 1, QTableWidgetItem(mode))
            self.sessions_table.setItem(i, 2, QTableWidgetItem(str(words_count)))
            self.sessions_table.setItem(i, 3, QTableWidgetItem(f"{score}%"))
            self.sessions_table.setItem(i, 4, QTableWidgetItem(str(duration)))

            self.sessions_table.setRowHeight(i, 20)

            self.sessions_table.item(i, 0).setData(
                Qt.ItemDataRole.UserRole,
                session_id
            )

        self.container.adjustSize()
        self.scroll.widget().adjustSize()

    # ================= HARD WORDS =================

    def load_hard_words(self):

        rows = self.training_repo.get_words_with_status()

        filtered = [
            (row[0], row[1], row[2])
            for row in rows
            if row[2] in ("Средне", "Плохо", "medium", "bad")
        ]

        self.words_table.setRowCount(len(filtered))

        for i, (word, wrong, status) in enumerate(filtered):
            self.words_table.setItem(i, 0, QTableWidgetItem(word))
            self.words_table.setItem(i, 1, QTableWidgetItem(str(wrong)))
            self.words_table.setItem(i, 2, QTableWidgetItem(status))

        self.container.adjustSize()
        self.scroll.widget().adjustSize()

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

    def load_chart(self):
        stats = self.training_repo.get_word_groups_stats()

        good = stats["good"]
        medium = stats["medium"]
        bad = stats["bad"]

        total = good + medium + bad
        if total == 0:
            return

        values = [
            good / total * 100,
            medium / total * 100,
            bad / total * 100
        ]

        labels = [
            f"Хорошо\n{good}",
            f"Средне\n{medium}",
            f"Плохо\n{bad}"
        ]

        self.ax.clear()
        self.apply_chart_theme()

        bars = self.ax.bar(labels, values)

        colors = (
            ["#2ecc71", "#f1c40f", "#e74c3c"]
            if not self.is_dark_theme()
            else ["#27ae60", "#f39c12", "#c0392b"]
        )

        for bar, color in zip(bars, colors):
            bar.set_color(color)

            height = bar.get_height()
            self.ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 1,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
                color="white" if self.is_dark_theme() else "black"
            )

        self.ax.set_ylim(0, 100)

        self.chart.figure.tight_layout()
        self.chart.draw()

    def apply_chart_theme(self):
        dark = self.is_dark_theme()

        if dark:
            bg = "#121212"
            text = "white"
            grid = "#2a2a2a"
        else:
            bg = "white"
            text = "black"
            grid = "#e0e0e0"

        fig = self.ax.figure

        # --- FIGURE background ---
        fig.patch.set_facecolor(bg)

        # --- AXES background ---
        self.ax.set_facecolor(bg)

        # --- TEXT ---
        self.ax.tick_params(colors=text)
        self.ax.title.set_color(text)
        self.ax.xaxis.label.set_color(text)
        self.ax.yaxis.label.set_color(text)

        for spine in self.ax.spines.values():
            spine.set_color(text)

        # --- GRID ---
        self.ax.grid(True, color=grid, alpha=0.3)

        # --- Qt canvas background ---
        self.chart.setStyleSheet(f"background-color: {bg};")

    def is_dark_theme(self):
        bg = self.palette().color(QPalette.ColorRole.Window)
        return bg.lightness() < 128

    def make_label_clean(self, label: QLabel):
        label.setStyleSheet("""
            QLabel {
                background: transparent;
                padding: 4px 0px;
                font-weight: 600;
            }
        """)

    def update_theme(self, theme):
        self.theme = theme
        self.delete_session_btn.setStyleSheet(
            danger_button_style(theme == "dark")
        )

    def adjust_table_height(self, table: QTableWidget):
        rows = table.rowCount()

        visible_rows = min(rows, MAX_TABLE_ROWS)

        height = HEADER_HEIGHT + visible_rows * ROW_HEIGHT + 2

        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        table.setMinimumHeight(height)
        table.setMaximumHeight(height)

        table.setFixedHeight(height)

        table.updateGeometry()
