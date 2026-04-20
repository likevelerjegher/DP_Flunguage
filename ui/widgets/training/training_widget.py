from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit


class TrainingWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.word_label = QLabel("Слово")
        self.input_field = QLineEdit()
        self.check_button = QPushButton("Проверить")
        self.result_label = QLabel("")

        layout.addWidget(self.word_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.check_button)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        # пока просто заглушка
        self.check_button.clicked.connect(self.check_answer)

    def check_answer(self):
        user_input = self.input_field.text()

        # временная логика
        if user_input.lower() == "test":
            self.result_label.setText("Правильно")
        else:
            self.result_label.setText("Неправильно")