from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Настройки")

        layout = QVBoxLayout()

        # ТЕМА
        self.theme_label = QLabel("Тема:")
        self.theme_box = QComboBox()
        self.theme_box.addItems(["light", "dark"])

        # ШРИФТ
        self.font_label = QLabel("Размер шрифта:")
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(14)

        # КНОПКА
        self.save_btn = QPushButton("Сохранить")

        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_box)
        layout.addWidget(self.font_label)
        layout.addWidget(self.font_size)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

        self.save_btn.clicked.connect(self.accept)

    def set_values(self, theme, font_size):
        self.theme_box.setCurrentText(theme)
        self.font_size.setValue(font_size)