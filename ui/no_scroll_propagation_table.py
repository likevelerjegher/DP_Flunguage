from PyQt6.QtWidgets import QTableWidget

class NoScrollPropagationTable(QTableWidget):
    def wheelEvent(self, event):
        # блокируем передачу скролла наружу (в QScrollArea)
        if self.verticalScrollBar().isVisible():
            super().wheelEvent(event)
        else:
            event.ignore()