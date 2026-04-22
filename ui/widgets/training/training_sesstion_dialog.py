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
        self.answered = False

        self.attempts = 0
        self.max_attempts = 3

        # ===== TIMER =====
        self.elapsed_seconds = 0
        self.word_start_time = 0

        self.setWindowTitle("Тренировка")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ===== TOP BAR =====
        top_bar = QHBoxLayout()

        self.progress_label = QLabel("1/1")
        self.timer_label = QLabel("00:00")

        top_bar.addWidget(self.progress_label)
        top_bar.addStretch()
        top_bar.addWidget(self.timer_label)

        self.layout.addLayout(top_bar)

        # ===== UI =====
        self.label_question = QLabel("")
        self.label_question.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.input = QLineEdit()
        self.label_result = QLabel("")
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_show = QPushButton("Показать ответ")
        self.btn_check = QPushButton("Проверить")
        self.btn_next = QPushButton("Дальше")

        self.options_layout = QVBoxLayout()

        self.layout.addWidget(self.label_question)
        self.layout.addWidget(self.input)
        self.layout.addLayout(self.options_layout)
        self.layout.addWidget(self.label_result)
        self.layout.addWidget(self.btn_check)
        self.layout.addWidget(self.btn_show)
        self.layout.addWidget(self.btn_next)

        # ===== TIMER =====
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # ===== EVENTS =====
        self.btn_check.clicked.connect(self.check_answer)
        self.btn_show.clicked.connect(self.show_answer)
        self.btn_next.clicked.connect(self.next_task)

        self.start_timer()
        self.load_task()

    # ================= TIMER =================

    def start_timer(self):
        self.elapsed_seconds = 0
        self.timer.start(1000)

    def stop_timer(self):
        self.timer.stop()

    def update_timer(self):
        self.elapsed_seconds += 1
        self.timer_label.setText(
            f"{self.elapsed_seconds // 60:02d}:{self.elapsed_seconds % 60:02d}"
        )

    # ================= TASK =================

    def load_task(self):
        self.answered = False
        self.attempts = 0

        self.clear_options()

        self.current_task = self.training_service.get_next_task()

        if not self.current_task:
            self.finish_training()
            return

        # ✅ ПРАВИЛЬНЫЙ ПРОГРЕСС
        completed = self.training_service.session["completed"]
        total = self.training_service.session["limit"]

        self.progress_label.setText(f"{completed}/{total}")

        self.label_result.setText("")
        self.input.clear()
        self.input.setEnabled(True)

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
                btn.clicked.connect(lambda _, o=option: self.process_choice(o))
                self.options_layout.addWidget(btn)

        self.label_question.setText(self.current_task["question"])

    # ================= ANSWER =================

    def process_choice(self, user_answer):
        if self.answered:
            return

        self.handle_answer(user_answer)

    def check_answer(self):
        if not self.current_task or self.answered:
            return

        user_answer = self.input.text()
        self.handle_answer(user_answer)

    def handle_answer(self, user_answer):
        is_correct = self.training_service.check_answer(
            self.current_task,
            user_answer
        )

        self.attempts += 1

        word_time = self.elapsed_seconds - self.word_start_time

        if is_correct:
            self.answered = True
            self.label_result.setText("✅ Правильно")

            self.training_service.update_progress(
                self.current_task["word"],
                True,
                word_time
            )

            self.finish_answer_ui()

        else:
            if self.current_task["mode"] == "input" and self.attempts < self.max_attempts:
                self.label_result.setText("❌ Неверно")
                return

            self.answered = True
            self.label_result.setText(
                f"❌ Неправильно\nОтвет: {self.current_task['answer']}"
            )

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

        self.label_result.setText(
            f"Ответ: {self.current_task['answer']}"
        )

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

        # дизейбл вариантов
        for i in range(self.options_layout.count()):
            btn = self.options_layout.itemAt(i).widget()
            if btn:
                btn.setEnabled(False)

                if btn.text() == self.current_task["answer"]:
                    btn.setStyleSheet("background-color: #4CAF50; color: white;")

    # ================= NEXT =================

    def next_task(self):
        if not self.answered:
            return
        self.load_task()

    # ================= FINISH =================

    def finish_training(self):
        self.stop_timer()

        self.training_service.finish_session()

        correct = self.training_service.session["correct"]
        total = self.training_service.session["limit"]

        percent = int((correct / total) * 100) if total else 0

        completed = self.training_service.session["completed"]
        total = self.training_service.session["limit"]

        self.progress_label.setText(f"{completed}/{total}")

        self.label_question.setText("Тренировка завершена 🎉")
        self.label_result.setText(
            f"Верных ответов: {percent}%"
        )

        self.input.hide()
        self.btn_check.hide()
        self.btn_next.hide()
        self.btn_show.hide()

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)

        self.layout.addWidget(btn_close)

    # ================= UTILS =================

    def clear_options(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()