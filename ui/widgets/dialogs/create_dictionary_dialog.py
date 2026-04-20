from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel


class CreateDictionaryDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Создать словарь")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название словаря")

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание")

        self.btn_create = QPushButton("Создать")

        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Описание"))
        layout.addWidget(self.desc_input)

        layout.addWidget(self.btn_create)

        self.setLayout(layout)

        self.btn_create.clicked.connect(self.accept)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "description": self.desc_input.text()
        }