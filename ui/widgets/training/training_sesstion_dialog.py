from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QLineEdit
)
from PyQt6.QtCore import Qt


class TrainingSessionDialog(QDialog):
    def __init__(self, training_service):
        super().__init__()
        self.training_service = training_service
        self.current_task = None

        self.setWindowTitle("Тренировка")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # вопрос
        self.label_question = QLabel("")
        self.label_question.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ввод
        self.input = QLineEdit()

        # результат
        self.label_result = QLabel("")
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # кнопки
        self.btn_check = QPushButton("Проверить")
        self.btn_next = QPushButton("Дальше")

        # варианты
        self.options_layout = QVBoxLayout()

        # layout
        self.layout.addWidget(self.label_question)
        self.layout.addWidget(self.input)
        self.layout.addLayout(self.options_layout)
        self.layout.addWidget(self.label_result)
        self.layout.addWidget(self.btn_check)
        self.layout.addWidget(self.btn_next)

        # events
        self.btn_check.clicked.connect(self.check_answer)
        self.btn_next.clicked.connect(self.load_task)

        self.load_task()

    def load_task(self):
        self.clear_options()

        self.current_task = self.training_service.get_next_task()

        if not self.current_task:
            self.label_question.setText("Тренировка завершена 🎉")
            self.input.hide()
            self.btn_check.hide()
            return

        self.label_result.setText("")
        self.input.clear()

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

    def process_answer(self, user_answer):
        is_correct = self.training_service.check_answer(self.current_task, user_answer)

        if is_correct:
            self.label_result.setText("✅ Правильно")
        else:
            self.label_result.setText(
                f"❌ Неправильно\nОтвет: {self.current_task['answer']}"
            )

        # ВАЖНО: теперь используем новый метод
        self.training_service.update_progress(
            self.current_task["word"],
            is_correct
        )

    def clear_options(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()