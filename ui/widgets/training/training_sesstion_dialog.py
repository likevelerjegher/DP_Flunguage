from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer


class TrainingSessionDialog(QDialog):
    def __init__(self, training_service):
        super().__init__()
        self.training_service = training_service

        self.current_task = None

        # ===== TIMER STATE =====
        self.elapsed_seconds = 0
        self.word_start_time = 0
        self.timer_running = False

        self.setWindowTitle("Тренировка")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ===== TOP TIMER BAR =====
        top_bar = QHBoxLayout()

        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        top_bar.addStretch()
        top_bar.addWidget(self.timer_label)

        self.layout.addLayout(top_bar)

        # ===== UI =====
        self.label_question = QLabel("")
        self.label_question.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.input = QLineEdit()
        self.label_result = QLabel("")
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_check = QPushButton("Проверить")
        self.btn_next = QPushButton("Дальше")

        self.options_layout = QVBoxLayout()

        self.layout.addWidget(self.label_question)
        self.layout.addWidget(self.input)
        self.layout.addLayout(self.options_layout)
        self.layout.addWidget(self.label_result)
        self.layout.addWidget(self.btn_check)
        self.layout.addWidget(self.btn_next)

        # ===== TIMER =====
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # ===== EVENTS =====
        self.btn_check.clicked.connect(self.check_answer)
        self.btn_next.clicked.connect(self.load_task)

        self.load_task()
        self.start_timer()

    # ================= TIMER =================

    def start_timer(self):
        self.elapsed_seconds = 0
        self.timer.start(1000)
        self.timer_running = True

    def stop_timer(self):
        self.timer.stop()
        self.timer_running = False

    def update_timer(self):
        self.elapsed_seconds += 1
        self.timer_label.setText(
            f"{self.elapsed_seconds // 60:02d}:{self.elapsed_seconds % 60:02d}"
        )

    # ================= TASKS =================

    def load_task(self):
        self.clear_options()

        self.current_task = self.training_service.get_next_task()

        if not self.current_task:
            self.label_question.setText("Тренировка завершена 🎉")
            self.input.hide()
            self.btn_check.hide()
            self.stop_timer()
            return

        self.label_result.setText("")
        self.input.clear()

        # старт времени на слово
        self.word_start_time = self.elapsed_seconds

        if self.current_task["mode"] == "input":
            self.input.show()
            self.label_question.setText(self.current_task["question"])
        else:
            self.input.hide()
            self.label_question.setText(self.current_task["question"])

            for option in self.current_task["options"]:
                btn = QPushButton(option)
                btn.clicked.connect(lambda _, o=option: self.process_answer(o))
                self.options_layout.addWidget(btn)

    def check_answer(self):
        if not self.current_task:
            return

        self.process_answer(self.input.text())

    # ================= ANSWER =================

    def process_answer(self, user_answer):
        is_correct = self.training_service.check_answer(
            self.current_task,
            user_answer
        )

        # время на слово
        word_time = self.elapsed_seconds - self.word_start_time

        if is_correct:
            self.label_result.setText(f"✅ Правильно)")
        else:
            self.label_result.setText(
                f"❌ Неправильно\nОтвет: {self.current_task['answer']}"
            )

        self.training_service.update_progress(
            self.current_task["word"],
            is_correct,
            word_time
        )

    # ================= UTILS =================

    def clear_options(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()