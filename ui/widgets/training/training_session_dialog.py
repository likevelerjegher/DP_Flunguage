from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QHBoxLayout, QFrame, QSizePolicy,
    QProgressBar
)
from PyQt6.QtCore import Qt, QTimer


class TrainingSessionDialog(QDialog):
    def __init__(self, training_service, theme="light"):
        super().__init__()

        self.training_service = training_service
        self.theme = theme

        self.current_task = None
        self.answered = False
        self.attempts = 0
        self.max_attempts = 3

        self.elapsed_seconds = 0
        self.word_start_time = 0

        self.setWindowTitle("Тренировка")
        self.resize(520, 420)
        self.setMinimumWidth(520)

        self._build_ui()
        self.apply_theme(self.theme)

        self.start_timer()
        self.load_task()

    def _build_ui(self):
        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(18, 18, 18, 18)
        self.main.setSpacing(12)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(8)

        top_bar = QHBoxLayout()
        self.progress_label = QLabel("0/0")
        self.timer_label = QLabel("00:00")

        top_bar.addWidget(self.progress_label)
        top_bar.addStretch()
        top_bar.addWidget(self.timer_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        header_layout.addLayout(top_bar)
        header_layout.addWidget(self.progress_bar)
        self.main.addWidget(header)

        question_card = QFrame()
        question_card.setObjectName("Card")
        question_layout = QVBoxLayout(question_card)
        question_layout.setContentsMargins(16, 18, 16, 18)

        self.label_question = QLabel("")
        self.label_question.setObjectName("Question")
        self.label_question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_question.setWordWrap(True)
        question_layout.addWidget(self.label_question)
        self.main.addWidget(question_card)

        answer_card = QFrame()
        answer_card.setObjectName("Card")
        answer_layout = QVBoxLayout(answer_card)
        answer_layout.setContentsMargins(16, 16, 16, 16)
        answer_layout.setSpacing(10)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите ответ")

        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(8)

        self.label_result = QLabel("")
        self.label_result.setObjectName("Result")
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_result.setWordWrap(True)

        self.btn_check = QPushButton("Проверить")
        self.btn_show = QPushButton("Показать ответ")
        self.btn_next = QPushButton("Дальше")

        self.btn_check.setObjectName("Primary")
        self.btn_show.setObjectName("Secondary")
        self.btn_next.setObjectName("Primary")

        self.btn_check.setAutoDefault(False)
        self.btn_show.setAutoDefault(False)
        self.btn_next.setAutoDefault(False)

        answer_layout.addWidget(self.input)
        answer_layout.addLayout(self.options_layout)
        answer_layout.addWidget(self.label_result)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(self.btn_check)
        buttons_row.addWidget(self.btn_show)
        buttons_row.addStretch()
        buttons_row.addWidget(self.btn_next)

        answer_layout.addLayout(buttons_row)
        self.main.addWidget(answer_card)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.btn_check.clicked.connect(self.check_answer)
        self.btn_show.clicked.connect(self.show_answer)
        self.btn_next.clicked.connect(self.next_task)

    def apply_theme(self, theme="light"):
        self.theme = theme
        is_dark = theme == "dark"

        if is_dark:
            bg = "#121212"
            card = "#1b1b1b"
            border = "#2b2b2b"
            text = "#f3f4f6"
            muted = "#9ca3af"
            input_bg = "#171717"
            input_border = "#3a3a3a"
            primary = "#2563eb"
            secondary = "#2a2a2a"
            option = "#2a2a2a"
            option_text = "#e5e7eb"
            disabled = "#2a2a2a"
            result_ok = "#22c55e"
            result_bad = "#ef4444"
            result_info = "#9ca3af"
        else:
            bg = "#f6f7fb"
            card = "#ffffff"
            border = "#dfe3ea"
            text = "#111827"
            muted = "#6b7280"
            input_bg = "#ffffff"
            input_border = "#cfd6e4"
            primary = "#2563eb"
            secondary = "#e8edf7"
            option = "#f3f4f6"
            option_text = "#1f2937"
            disabled = "#f3f4f6"
            result_ok = "#16a34a"
            result_bad = "#dc2626"
            result_info = "#6b7280"

        self.colors = {
            "bg": bg,
            "card": card,
            "border": border,
            "text": text,
            "muted": muted,
            "input_bg": input_bg,
            "input_border": input_border,
            "primary": primary,
            "secondary": secondary,
            "option": option,
            "option_text": option_text,
            "disabled": disabled,
            "result_ok": result_ok,
            "result_bad": result_bad,
            "result_info": result_info,
        }

        self.setStyleSheet(f"""
            QDialog {{
                background: {bg};
            }}
            QFrame#Card {{
                background: {card};
                border: 1px solid {border};
                border-radius: 14px;
            }}
            QLabel {{
                color: {text};
            }}
            QLabel#Question {{
                font-size: 16px;
                font-weight: 600;
            }}
            QLabel#Result {{
                font-size: 14px;
                font-weight: 600;
            }}
            QLineEdit {{
                padding: 10px;
                border: 1px solid {input_border};
                border-radius: 10px;
                background: {input_bg};
                color: {text};
            }}
            QPushButton {{
                padding: 10px 14px;
                border-radius: 10px;
                border: none;
            }}
            QPushButton#Primary {{
                background: {primary};
                color: white;
            }}
            QPushButton#Secondary {{
                background: {secondary};
                color: {text};
            }}
            QPushButton#Option {{
                background: {option};
                color: {option_text};
                text-align: left;
                padding-left: 14px;
            }}
            QPushButton#Option:disabled {{
                background: {disabled};
                color: {muted};
            }}
            QProgressBar {{
                border: 1px solid {input_border};
                border-radius: 8px;
                background: {disabled};
                text-align: center;
                color: {text};
                height: 18px;
            }}
            QProgressBar::chunk {{
                background: #22c55e;
                border-radius: 8px;
            }}
        """)

    def update_theme(self, theme):
        self.apply_theme(theme)
        self._refresh_visible_controls()

    def _refresh_visible_controls(self):
        if self.current_task and self.current_task.get("mode") == "input":
            self.btn_check.setStyleSheet("")
            self.btn_show.setStyleSheet("")
        self.btn_next.setStyleSheet("")

    def start_timer(self):
        self.elapsed_seconds = 0
        self.timer.start(1000)
        self.timer_label.setText("00:00")

    def stop_timer(self):
        self.timer.stop()

    def update_timer(self):
        self.elapsed_seconds += 1
        self.timer_label.setText(
            f"{self.elapsed_seconds // 60:02d}:{self.elapsed_seconds % 60:02d}"
        )

    def load_task(self):
        self.answered = False
        self.attempts = 0
        self.clear_options()

        self.current_task = self.training_service.get_next_task()

        if not self.current_task:
            self.finish_training()
            return

        completed = self.training_service.session["completed"]
        total = self.training_service.session["limit"]

        self.progress_label.setText(f"{completed}/{total}")
        self.progress_bar.setValue(int((completed / total) * 100) if total else 0)

        self.label_result.setText("")
        self.label_result.setStyleSheet(f"color: {self.colors['muted']}; font-weight: 600;")
        self.input.clear()
        self.input.setEnabled(True)
        self.input.setStyleSheet("")
        self.word_start_time = self.elapsed_seconds

        self.btn_next.hide()
        self.btn_check.hide()
        self.btn_show.hide()

        if self.current_task["mode"] == "input":
            self.input.show()
            self.btn_check.show()
            self.btn_show.show()
        else:
            self.input.hide()
            for option in self.current_task["options"]:
                btn = QPushButton(option)
                btn.setObjectName("Option")
                btn.setAutoDefault(False)
                btn.setDefault(False)
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda _, o=option: self.process_choice(o))
                self.options_layout.addWidget(btn)

        self.label_question.setText(self.current_task["question"])

    def process_choice(self, user_answer):
        if self.answered:
            return
        self.handle_answer(user_answer)

    def check_answer(self):
        if not self.current_task or self.answered:
            return
        self.handle_answer(self.input.text())

    def handle_answer(self, user_answer):
        is_correct = self.training_service.check_answer(self.current_task, user_answer)
        self.attempts += 1
        word_time = self.elapsed_seconds - self.word_start_time

        if is_correct:
            self.answered = True
            self.label_result.setText("Правильно")
            self.label_result.setStyleSheet(f"color: {self.colors['result_ok']}; font-weight: 700;")

            self.training_service.update_progress(
                self.current_task["word"],
                True,
                word_time
            )
            self.finish_answer_ui()
            return

        if self.current_task["mode"] == "input" and self.attempts < self.max_attempts:
            self.label_result.setText("Неверно, попробуйте ещё раз")
            self.label_result.setStyleSheet(f"color: {self.colors['result_bad']}; font-weight: 700;")
            return

        self.answered = True
        self.label_result.setText(f"Неправильно. Ответ: {self.current_task['answer']}")
        self.label_result.setStyleSheet(f"color: {self.colors['result_bad']}; font-weight: 700;")

        self.training_service.update_progress(
            self.current_task["word"],
            False,
            word_time
        )
        self.finish_answer_ui()

    def show_answer(self):
        if not self.current_task or self.answered:
            return

        self.answered = True
        self.label_result.setText(f"Ответ: {self.current_task['answer']}")
        self.label_result.setStyleSheet(f"color: {self.colors['result_info']}; font-weight: 700;")

        word_time = self.elapsed_seconds - self.word_start_time
        self.training_service.update_progress(
            self.current_task["word"],
            False,
            word_time
        )
        self.finish_answer_ui()

    def finish_answer_ui(self):
        self.input.setEnabled(False)
        self.btn_check.hide()
        self.btn_show.hide()
        self.btn_next.show()

        for i in range(self.options_layout.count()):
            btn = self.options_layout.itemAt(i).widget()
            if btn:
                btn.setEnabled(False)
                if btn.text() == self.current_task["answer"]:
                    btn.setStyleSheet("""
                        QPushButton {
                            background: #22c55e;
                            color: white;
                            padding: 10px 14px;
                            border-radius: 10px;
                            text-align: left;
                        }
                    """)

    def next_task(self):
        if not self.answered:
            return
        self.load_task()

    def finish_training(self):
        self.stop_timer()
        self.training_service.finish_session()

        correct = self.training_service.session["correct"]
        total = self.training_service.session["limit"]
        percent = int((correct / total) * 100) if total else 0

        completed = self.training_service.session["completed"]
        self.progress_label.setText(f"{completed}/{total}")
        self.progress_bar.setValue(100)

        self.label_question.setText("Тренировка завершена")
        self.label_result.setText(f"Верных ответов: {percent}%")
        self.label_result.setStyleSheet(f"color: {self.colors['primary']}; font-weight: 700;")

        self.input.hide()
        self.btn_check.hide()
        self.btn_next.hide()
        self.btn_show.hide()

        btn_close = QPushButton("Закрыть")
        btn_close.setObjectName("Primary")
        btn_close.setAutoDefault(False)
        btn_close.setDefault(False)
        btn_close.clicked.connect(self.accept)
        self.main.addWidget(btn_close)

    def clear_options(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
