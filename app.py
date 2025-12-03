import sys
import globals
from skull_finder import SkullFinder

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QToolButton, QWidget, QGridLayout, QMessageBox


class CellButton(QToolButton):

    def __init__(self, row: int, col: int, skull_finder: SkullFinder = None, window=None, parent=None):
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
            case 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
                self.setIcon(QPixmap(f"assets/cell-64x64-{data}.png"))
            case globals.CELL_UNEXPLORED:
                self.setIcon(QPixmap("assets/cell-64x64-blank.png"))
            case globals.CELL_EXPLORED_SKULL:
                self.setIcon(QPixmap("assets/cell-64x64-skull.png"))
            case _:
                raise ValueError(f"Invalid data value: {data}")

    def on_click(self):
        print(f"Button Clicked: {self.get_coordinates()}")
        self.skull_finder.explore_cell(self.row, self.col)
        self.window.selected_row, self.window.selected_col = self.get_coordinates()
        self.window.update_grid(self.row, self.col)

        if self.skull_finder.status == globals.WIN:
            self.window.win()
        elif self.skull_finder.status == globals.LOSE:
            self.window.lose()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Skull Solver")
        # self.setFixedSize(QSize(500, 500))

        central = QWidget()
        self.layout = QGridLayout(central)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central)

        self.skull_finder = SkullFinder(row_size=7, col_size=7)
        self.skull_finder.fill_grid()
        self.selected_row = self.skull_finder.row_size
        self.selected_col = 0

        self.grid = []
        for row in range(0, self.skull_finder.row_size):
            button_row = []
            for col in range(0, self.skull_finder.col_size):
                button = CellButton(row=row, col=col, skull_finder=self.skull_finder, window=self)
                self.layout.addWidget(button, row, col)
                button_row.append(button)

            self.grid.append(button_row)

        self.update_grid(self.selected_row, self.selected_col)

    def update_grid(self, selected_row: int, selected_col: int, allow_diagonal: bool = False):
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.grid[row][col].update_icon(self.skull_finder.grid_displayed_data[row][col])
                self.grid[row][col].setDisabled(True)

        if selected_row == self.skull_finder.row_size:
            # Currently off the board, under the bottom row. Enable all bottom row cells
            for col in range(0, self.skull_finder.col_size):
                self.grid[selected_row - 1][col].setDisabled(False)

        else:
            # Currently on the board. Enable adjacent cells only. Diagonal cells are enabled if allow_diagonal is True
            for x in range(-1, 2):
                if not self.skull_finder.valid_row(selected_row + x):
                    continue

                for y in range(-1, 2):
                    if not self.skull_finder.valid_col(selected_col + y):
                        continue

                    if allow_diagonal is False and abs(x) == abs(y):
                        continue

                    self.grid[selected_row + x][selected_col + y].setDisabled(False)

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key.Key_Left | Qt.Key.Key_A:
                # Currently off the board
                if not self.skull_finder.valid_row(self.selected_row):
                    return

                if self.skull_finder.valid_col(self.selected_col - 1):
                    self.grid[self.selected_row][self.selected_col - 1].on_click()

            case Qt.Key.Key_Right | Qt.Key.Key_D:
                # Currently off the board
                if not self.skull_finder.valid_row(self.selected_row):
                    return

                if self.skull_finder.valid_col(self.selected_col + 1):
                    self.grid[self.selected_row][self.selected_col + 1].on_click()

            case Qt.Key.Key_Up | Qt.Key.Key_W:
                # Currently off the board in the starting area, move to middle column
                if self.selected_row == self.skull_finder.row_size:
                    self.grid[self.selected_row - 1][self.skull_finder.col_size // 2].on_click()

                elif self.skull_finder.valid_row(self.selected_row - 1):
                    self.grid[self.selected_row - 1][self.selected_col].on_click()

            case Qt.Key.Key_Down | Qt.Key.Key_S:
                if self.skull_finder.valid_row(self.selected_row + 1):
                    self.grid[self.selected_row + 1][self.selected_col].on_click()
                else:
                    # Go off the board into the starting area
                    self.selected_row = self.skull_finder.row_size
                    self.update_grid(self.selected_row, self.selected_col)

    def win(self):
        self.skull_finder.reveal_all()
        self.update_grid(self.selected_row, self.selected_col)
        message = QMessageBox.information(self, "You Win!", "You Win!")
        self.restart()

    def lose(self):
        self.skull_finder.reveal_all()
        self.update_grid(self.selected_row, self.selected_col)
        message = QMessageBox.information(self, "You Lose!", "You Lose!")
        self.restart()

    def restart(self):
        self.skull_finder = SkullFinder(row_size=7, col_size=7)
        self.skull_finder.fill_grid()
        self.skull_finder.status = globals.PLAYING
        self.selected_row = self.skull_finder.row_size
        self.selected_col = 0

        # Replace the completed connected skull finder object with the new one for each button
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.grid[row][col].skull_finder = self.skull_finder

        self.update_grid(self.selected_row, self.selected_col)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    app.exec()
