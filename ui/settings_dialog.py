from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QSpinBox,
    QPushButton, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Настройки")
        self.setMinimumWidth(320)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ===== CARD: Theme =====
        theme_card = QFrame()
        theme_card.setStyleSheet(self.card_style())

        theme_layout = QVBoxLayout(theme_card)

        theme_title = QLabel("Тема")
        self.theme_box = QComboBox()
        self.theme_box.addItems(["light", "dark"])

        theme_layout.addWidget(theme_title)
        theme_layout.addWidget(self.theme_box)

        # ===== CARD: Font =====
        font_card = QFrame()
        font_card.setStyleSheet(self.card_style())

        font_layout = QVBoxLayout(font_card)

        font_title = QLabel("Размер шрифта")
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(14)

        font_layout.addWidget(font_title)
        font_layout.addWidget(self.font_size)

        # ===== BUTTON =====
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet(self.button_style())

        btn_layout.addWidget(self.save_btn)

        # ===== ADD =====
        main_layout.addWidget(theme_card)
        main_layout.addWidget(font_card)
        main_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)

    def set_values(self, theme, font_size):
        self.theme_box.setCurrentText(theme)
        self.font_size.setValue(font_size)

    # ===== STYLES =====
    def card_style(self):
        return """
        QFrame {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 10px;
        }
        QLabel {
            font-weight: 600;
        }
        """

    def button_style(self):
        return """
        QPushButton {
            background-color: #2ecc71;
            color: white;
            border-radius: 6px;
            padding: 6px 14px;
        }
        QPushButton:hover {
            background-color: #27ae60;
        }
        """