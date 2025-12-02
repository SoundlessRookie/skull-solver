import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QToolButton


class CellButton(QToolButton):
    CELL_EXPLORED_BLANK = 0
    CELL_UNEXPLORED = -1
    CELL_EXPLORED_SKULL = -2

    def __init__(self, row: int, col: int):
        super().__init__()
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.row = row
        self.col = col
        self.setFixedSize(QSize(64, 64))
        self.setIconSize(QSize(64, 64))
        self.setDisabled(True)
        self.setCheckable(True)
        self.update_icon(self.CELL_UNEXPLORED)
        self.clicked.connect(self.on_click)

    def get_coordinates(self):
        return self.row, self.col

    def update_icon(self, data: int):
        match data:
            case self.CELL_EXPLORED_BLANK:
                self.setIcon(QPixmap("assets/cell-64x64-0.png"))
            case 1:
                self.setIcon(QPixmap("assets/cell-64x64-1.png"))
            case 2:
                self.setIcon(QPixmap("assets/cell-64x64-2.png"))
            case 3:
                self.setIcon(QPixmap("assets/cell-64x64-3.png"))
            case 4:
                self.setIcon(QPixmap("assets/cell-64x64-4.png"))
            case 5:
                self.setIcon(QPixmap("assets/cell-64x64-5.png"))
            case 6:
                self.setIcon(QPixmap("assets/cell-64x64-6.png"))
            case 7:
                self.setIcon(QPixmap("assets/cell-64x64-7.png"))
            case 8:
                self.setIcon(QPixmap("assets/cell-64x64-8.png"))
            case 9:
                self.setIcon(QPixmap("assets/cell-64x64-9.png"))
            case 10:
                self.setIcon(QPixmap("assets/cell-64x64-10.png"))
            case self.CELL_UNEXPLORED:
                self.setIcon(QPixmap("assets/cell-64x64-blank.png"))
            case self.CELL_EXPLORED_SKULL:
                self.setIcon(QPixmap("assets/cell-64x64-skull.png"))
            case _:
                raise ValueError(f"Invalid data value: {data}")

    def on_click(self):
        print(f"Button Clicked: {self.get_coordinates()}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Skull Solver")
        self.setFixedSize(QSize(500, 500))

        # TODO: Create grid
        button = CellButton(0, 0)
        button.setDisabled(False)
        self.setCentralWidget(button)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
