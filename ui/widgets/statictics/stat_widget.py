from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox, QHBoxLayout, QScrollArea, QSizePolicy, QSpacerItem,
    QToolTip, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.no_scroll_propagation_table import NoScrollPropagationTable
from ui.styles.button_styles import danger_button_style

from datetime import datetime
from ui.widgets.statictics.stat_table_widget_item import NumericTableWidgetItem
import qtawesome as qta

MAX_TABLE_ROWS = 8
ROW_HEIGHT = 20
HEADER_HEIGHT = 25


class StatWidget(QWidget):
    def __init__(self, training_repo):
        super().__init__()

        self.training_repo = training_repo
        QToolTip.setFont(QFont("Arial", 12))

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
        general_container = QFrame()
        general_container_layout = QVBoxLayout(general_container)
        general_container_layout.setContentsMargins(12, 0, 0, 0)

        self.general_label = QLabel()
        self.general_label.setStyleSheet("""
            QLabel {
                padding: 8px 12px;
                border-left: 3px solid #888;
                background: rgba(128, 128, 128, 0.06);
                border-radius: 0px;
                line-height: 1.6;
            }
        """)

        general_container_layout.addWidget(self.general_label)
        self.layout.addWidget(general_container)

        # ===== TITLE =====
        title_row = QHBoxLayout()

        label_hard = QLabel("Уровень усвоения слов")
        self.make_label_clean(label_hard)

        self.info_btn = QPushButton()
        self.info_btn.setFlat(True)
        self.info_btn.setFixedSize(20, 20)
        self.info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.info_btn.setIcon(qta.icon('fa5s.info-circle', color="#888"))

        # текст подсказки
        self.info_btn.setToolTip("""
            <b>Статусы слов:</b><br><br>
            <b>new</b> — слово ещё не изучалось<br>
            <b>medium</b> — средний уровень<br>
            <b>bad</b> — слово запоминается плохо<br>
            <b>good</b> — слово хорошо усвоено<br><br>
    
            <b>Логика:</b><br>
            &lt; 3 ответов → medium<br>
            accuracy &lt; 60% → bad<br>
            accuracy ≥ 60% → medium<br>
            accuracy ≥ 80% + ≥5 ответов → good
        """)

        title_row.addWidget(label_hard)
        title_row.addWidget(self.info_btn)
        title_row.addStretch()

        self.layout.addSpacing(15)
        self.layout.addLayout(title_row)

        # ===== CHART =====

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
        self.words_table.setColumnCount(4)
        self.words_table.setSortingEnabled(True)

        self.words_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        self.words_table.setHorizontalHeaderLabels([
            "Слово", "Верно", "Ошибки", "Статус"
        ])

        header = self.words_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

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

    def _format_date(self, date_str):
        try:
            return datetime.fromisoformat(date_str).strftime("%d.%m.%Y %H:%M")
        except Exception:
            return date_str[:16]

    def load_sessions(self):
        rows = self.training_repo.get_last_sessions()

        self.sessions_table.setRowCount(len(rows))

        for i, (session_id, date, mode, words_count, score, duration) in enumerate(rows):
            self.sessions_table.setItem(i, 0, QTableWidgetItem(self._format_date(date)))
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
            (word, correct, wrong, status)
            for word, correct, wrong, status in rows
            if status in ("medium", "bad")
        ]

        self.words_table.setSortingEnabled(False)
        self.words_table.setRowCount(len(filtered))

        for i, (word, correct, wrong, status) in enumerate(filtered):
            word_item = QTableWidgetItem(word)
            correct_item = NumericTableWidgetItem(str(correct))
            wrong_item = NumericTableWidgetItem(str(wrong))
            status_item = QTableWidgetItem(status)

            correct_item.setData(Qt.ItemDataRole.UserRole, correct)
            wrong_item.setData(Qt.ItemDataRole.UserRole, wrong)

            self.words_table.setItem(i, 0, word_item)
            self.words_table.setItem(i, 1, correct_item)
            self.words_table.setItem(i, 2, wrong_item)
            self.words_table.setItem(i, 3, status_item)

        self.words_table.setSortingEnabled(True)
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

        new = stats["new"]
        good = stats["good"]
        medium = stats["medium"]
        bad = stats["bad"]

        total = new + good + medium + bad

        if total == 0:
            return

        values = [
            new / total * 100,
            good / total * 100,
            medium / total * 100,
            bad / total * 100
        ]

        labels = [
            f"Новые\n{new}",
            f"Хорошо\n{good}",
            f"Средне\n{medium}",
            f"Плохо\n{bad}"
        ]

        self.ax.clear()
        self.apply_chart_theme()

        bars = self.ax.bar(labels, values)

        colors = (
            ["#3498db", "#2ecc71", "#f1c40f", "#e74c3c"]
            if not self.is_dark_theme()
            else ["#2980b9", "#27ae60", "#f39c12", "#c0392b"]
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

        self.ax.title.set_color(text)

        for label in self.ax.get_xticklabels():
            label.set_color(text)

        for label in self.ax.get_yticklabels():
            label.set_color(text)

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
