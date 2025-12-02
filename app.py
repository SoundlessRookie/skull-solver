import sys
import globals
from skull_finder import SkullFinder

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QToolButton, QWidget, QGridLayout


class CellButton(QToolButton):

    def __init__(self, row: int, col: int, skull_finder: SkullFinder = None, window: QWidget = None, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.row = row
        self.col = col
        self.skull_finder = skull_finder
        self.window = window
        self.setFixedSize(QSize(64, 64))
        self.setIconSize(QSize(64, 64))
        self.setDisabled(True)
        self.setCheckable(False)
        self.update_icon(globals.CELL_UNEXPLORED)
        self.clicked.connect(self.on_click)

    def get_coordinates(self):
        return self.row, self.col

    def update_icon(self, data: int):
        match data:
            case globals.CELL_EXPLORED_BLANK:
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
            case globals.CELL_UNEXPLORED:
                self.setIcon(QPixmap("assets/cell-64x64-blank.png"))
            case globals.CELL_EXPLORED_SKULL:
                self.setIcon(QPixmap("assets/cell-64x64-skull.png"))
            case _:
                raise ValueError(f"Invalid data value: {data}")

    def on_click(self):
        print(f"Button Clicked: {self.get_coordinates()}")
        self.skull_finder.explore_cell(self.row, self.col)
        self.window.update_grid()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Skull Solver")
        # self.setFixedSize(QSize(500, 500))

        central = QWidget()
        layout = QGridLayout(central)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central)

        self.skull_finder = SkullFinder(row_size=7, col_size=7)
        self.skull_finder.fill_grid()

        self.grid = []
        for row in range(0, self.skull_finder.row_size):
            button_row = []
            for col in range(0, self.skull_finder.col_size):
                button = CellButton(row=row, col=col, skull_finder=self.skull_finder, window=self)
                button.setDisabled(False)
                layout.addWidget(button, row, col)
                button_row.append(button)

            self.grid.append(button_row)

    def update_grid(self):
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.grid[row][col].update_icon(self.skull_finder.grid_displayed_data[row][col])


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
