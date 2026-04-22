from PyQt6.QtWidgets import QTableWidget


class AutoHeightTable(QTableWidget):
    def __init__(self, max_rows=8, row_height=20, header_height=25, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_rows = max_rows
        self.row_height = row_height
        self.header_height = header_height

    def sizeHint(self):
        rows = self.rowCount()
        visible_rows = min(rows, self.max_rows)

        height = self.header_height + visible_rows * self.row_height + 2

        return self.minimumSizeHint().expandedTo(
            self.minimumSizeHint().scaled(0, height)
        )

    def update_height(self):
        self.setMinimumHeight(
            self.header_height +
            min(self.rowCount(), self.max_rows) * self.row_height + 2
        )
        self.updateGeometry()