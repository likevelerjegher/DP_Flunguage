from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class StatisticsWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.label = QLabel("Статистика обучения")
        self.refresh_button = QPushButton("Обновить")

        layout.addWidget(self.label)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

        self.refresh_button.clicked.connect(self.load_stats)

    def load_stats(self):
        # заглушка
        self.label.setText("Прогресс: 75%")