from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import qtawesome as qta


# КАСТОМНАЯ КНОПКА
class NavButton(QWidget):
    def __init__(self, icon_name, text):
        super().__init__()

        self.icon_name = icon_name
        self.text = text

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(3)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

        self.setLayout(layout)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def update_icon(self, color):
        icon = qta.icon(self.icon_name, color=color)
        self.icon_label.setPixmap(icon.pixmap(24, 24))

    def set_active(self, active, active_color, inactive_color):
        if active:
            self.update_icon(active_color)
            self.text_label.setStyleSheet(f"color: {active_color};")
        else:
            self.update_icon(inactive_color)
            self.text_label.setStyleSheet(f"color: {inactive_color};")