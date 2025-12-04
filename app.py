import sys
import globals
from skull_finder import SkullFinder

from PySide6.QtCore import QSize, Qt, QTimer
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
        self.window.update_button_grid(self.row, self.col)

        if self.skull_finder.status == globals.WIN:
            self.window.win()
        elif self.skull_finder.status == globals.LOSE:
            self.window.lose()


class GoalButton(QToolButton):

    def __init__(self, skull_finder: SkullFinder = None, window=None, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.skull_finder = skull_finder
        self.window = window
        self.setFixedSize(QSize(448, 64))
        self.setIconSize(QSize(448, 64))
        self.setDisabled(True)
        self.setCheckable(False)
        self.setIcon(QPixmap("assets/goal.png"))
        self.clicked.connect(self.on_click)

    def on_click(self):
        print(f"Button Clicked: Goal!")
        self.skull_finder.explore_cell(globals.ABOVE_TOP_ROW, -1)
        self.window.selected_row, self.window.selected_col = (globals.ABOVE_TOP_ROW, -1)
        self.window.disable_button_grid()
        self.window.win()


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

        # Auto grid assesses each cell by risk level from 0 to 1.
        self.auto_grid = []
        for _ in range(self.skull_finder.row_size):
            row = [{"risk": 1, "flag": False} for _ in range(self.skull_finder.col_size)]
            self.auto_grid.append(row)

        self.button_grid = []
        for row in range(0, self.skull_finder.row_size):
            button_row = []
            for col in range(0, self.skull_finder.col_size):
                button = CellButton(row=row, col=col, skull_finder=self.skull_finder, window=self)
                self.layout.addWidget(button, row + 1, col)
                button_row.append(button)

            self.button_grid.append(button_row)

        self.update_button_grid(self.selected_row, self.selected_col)

        self.auto_running = False
        self.option_auto = False
        self.button_auto = QToolButton()
        self.button_auto.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_auto.setText("Auto")
        self.button_auto.setCheckable(True)
        self.button_auto.setFixedSize(QSize(64, 64))
        self.button_auto.setIcon(QPixmap("assets/auto.png"))
        self.button_auto.setIconSize(QSize(32, 32))
        self.button_auto.clicked.connect(self.toggle_auto)
        self.layout.addWidget(self.button_auto, 8, 3)

        self.move_timer = QTimer()
        self.move_timer.setInterval(1000)
        self.current_move_index = 0

        self.button_goal = GoalButton(skull_finder=self.skull_finder, window=self)
        self.layout.addWidget(self.button_goal, 0, 0, 1, 7)

    def toggle_auto(self):
        if self.button_auto.isChecked():
            self.option_auto = True
            self.auto_solve()
        else:
            self.button_auto.setDisabled(True)
            self.option_auto = False

    def update_button_grid(self, selected_row: int, selected_col: int, allow_diagonal: bool = False):
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.button_grid[row][col].update_icon(self.skull_finder.grid_displayed_data[row][col])
                self.button_grid[row][col].setDisabled(True)

        if selected_row == self.skull_finder.row_size:
            # Currently off the board, under the bottom row. Enable all bottom row cells
            for col in range(0, self.skull_finder.col_size):
                self.button_grid[selected_row - 1][col].setDisabled(False)

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

                    self.button_grid[selected_row + x][selected_col + y].setDisabled(False)

            if selected_row == globals.TOP_ROW:
                self.button_goal.setDisabled(False)
            else:
                self.button_goal.setDisabled(True)

    def disable_button_grid(self):
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.button_grid[row][col].setDisabled(True)

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key.Key_A:
                # Currently off the board
                if not self.skull_finder.valid_row(self.selected_row):
                    return

                if self.skull_finder.valid_col(self.selected_col - 1):
                    self.button_grid[self.selected_row][self.selected_col - 1].on_click()

            case Qt.Key.Key_D:
                # Currently off the board
                if not self.skull_finder.valid_row(self.selected_row):
                    return

                if self.skull_finder.valid_col(self.selected_col + 1):
                    self.button_grid[self.selected_row][self.selected_col + 1].on_click()

            case Qt.Key.Key_W:
                # Currently off the board in the starting area, move to middle column
                if self.selected_row == self.skull_finder.row_size:
                    self.button_grid[self.selected_row - 1][self.skull_finder.col_size // 2].on_click()

                # Currently moving up from the top row to the goal
                elif self.selected_row == globals.TOP_ROW:
                    self.button_goal.on_click()

                # Elsewhere on the board
                elif self.skull_finder.valid_row(self.selected_row - 1):
                    self.button_grid[self.selected_row - 1][self.selected_col].on_click()

            case Qt.Key.Key_S:
                if self.skull_finder.valid_row(self.selected_row + 1):
                    self.button_grid[self.selected_row + 1][self.selected_col].on_click()
                else:
                    # Go off the board into the starting area
                    self.selected_row = self.skull_finder.row_size
                    self.update_button_grid(self.selected_row, self.selected_col)

    def win(self):
        self.skull_finder.reveal_all()
        self.update_button_grid(self.selected_row, self.selected_col)
        QMessageBox.information(self, "You Win!", "You Win!")
        self.restart()

    def lose(self):
        self.skull_finder.reveal_all()
        self.update_button_grid(self.selected_row, self.selected_col)
        QMessageBox.information(self, "You Lose!", "You Lose!")
        self.restart()

    def restart(self):
        self.option_auto = False
        self.auto_running = False
        self.button_auto.setChecked(False)
        self.button_auto.setDisabled(False)
        self.skull_finder = SkullFinder(row_size=7, col_size=7)
        self.skull_finder.fill_grid()
        self.skull_finder.status = globals.PLAYING
        self.selected_row = self.skull_finder.row_size
        self.selected_col = 0

        # Replace the completed connected skull finder object with the new one for each button
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                self.button_grid[row][col].skull_finder = self.skull_finder

        self.update_button_grid(self.selected_row, self.selected_col)

    # def auto_solve(self):
    #     self.auto_running = True
#
    #     while self.skull_finder.status == globals.PLAYING and self.option_auto:
    #         destinations = self.analyze_board()
    #         print("Destinations:", destinations)
#
    #         while len(destinations) > 0 and self.skull_finder.status == globals.PLAYING and self.option_auto:
    #             destination = destinations.pop(0)
    #             print("Moving to:", destination["row"], destination["col"])
    #             self.button_grid[destination["row"]][destination["col"]].on_click()
    #             # TODO Delay without blocking the rest of the app
#
    #     self.auto_running = False
    #     self.button_auto.setDisabled(False)

    def auto_solve(self):
        # TODO Fix logic
        self.auto_running = True
        destinations = self.analyze_board()
        print("Destinations:", destinations)

        self.move_timer.timeout.connect(lambda: self.auto_move(destinations))

        if destinations:
            self.move_timer.start()

    def auto_move(self, destinations):
        # TODO Fix logic
        if (self.current_move_index < len(destinations) and
                self.skull_finder.status == globals.PLAYING and
                self.option_auto):
            destination = destinations[0]
            print("Moving to:", destination["row"], destination["col"])
            self.button_grid[destination["row"]][destination["col"]].on_click()
            self.current_move_index += 1
        else:
            self.move_timer.stop()
            self.auto_running = False
            self.button_auto.setDisabled(False)

            if self.skull_finder.status == globals.PLAYING and self.option_auto:
                self.auto_solve()

    def analyze_board(self):
        # TODO Fix logic
        destinations = []
        # Loop 1: Look for guaranteed skulls and safe spaces based on a single cell's neighbors
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                value = self.skull_finder.grid_displayed_data[row][col]

                if value in range(1, 9) and value == self.skull_finder.sum_neighboring_unexplored(row, col):
                    # Neighboring unexplored cells are guaranteed to be skulls, set risk to 1 and flag them

                    for x in range(-1, 2):
                        if not self.skull_finder.valid_row(row + x):
                            continue

                        for y in range(-1, 2):
                            if not self.skull_finder.valid_col(col + y):
                                continue

                            if self.skull_finder.grid_displayed_data[row + x][col + y] == globals.CELL_UNEXPLORED:
                                self.auto_grid[row + x][col + y]["risk"] = 1
                                self.auto_grid[row + x][col + y]["flag"] = True

                if value in range(1, 9) and value == self.sum_flagged_neighboring(row, col):
                    # Non-flagged neighboring cells are guaranteed to be safe, set risk to 0 amd add to destinations

                    for x in range(-1, 2):
                        if not self.skull_finder.valid_row(row + x):
                            continue

                        for y in range(-1, 2):
                            if not self.skull_finder.valid_col(col + y):
                                continue

                            if not self.auto_grid[row + x][col + y]["flag"]:
                                self.auto_grid[row + x][col + y]["risk"] = 0
                                if {"row": row + x, "col": col + y} not in destinations:
                                    destinations.append({"row": row + x, "col": col + y})

        # Loop 2: Look for guaranteed skulls and safe spaces based on two numbered adjacent cells' neighbors
        for row in range(0, self.skull_finder.row_size):
            for col in range(0, self.skull_finder.col_size):
                if self.skull_finder.grid_displayed_data[row][col] not in range(1, 9):
                    continue

                for x in range(-1, 2):
                    if not self.skull_finder.valid_row(row + x):
                        continue

                    for y in range(-1, 2):
                        if not self.skull_finder.valid_col(col + y):
                            continue

                        if abs(x) == abs(y):
                            continue

                        row_2 = row + x
                        col_2 = col + y

                        nonflagged_neighbors_a = self.get_unexplored_nonflagged_neighbors(row, col)
                        nonflagged_neighbors_b = self.get_unexplored_nonflagged_neighbors(row_2, col_2)

                        exclusive_neighbors_a = [cell for cell in nonflagged_neighbors_a if cell not in nonflagged_neighbors_b]
                        exclusive_neighbors_b = [cell for cell in nonflagged_neighbors_b if cell not in nonflagged_neighbors_a]

                        modified_value_a = self.skull_finder.grid_displayed_data[row][col] - self.sum_flagged_neighboring(row, col)
                        modified_value_b = self.skull_finder.grid_displayed_data[row_2][col_2] - self.sum_flagged_neighboring(row_2, col_2)

                        if modified_value_a - modified_value_b == len(exclusive_neighbors_a):
                            for neighbor in exclusive_neighbors_a:
                                self.auto_grid[neighbor["row"]][neighbor["col"]]["risk"] = 1
                                self.auto_grid[neighbor["row"]][neighbor["col"]]["flag"] = True

                            for neighbor in exclusive_neighbors_b:
                                self.auto_grid[neighbor["row"]][neighbor["col"]]["risk"] = 0
                                if {"row": neighbor["row"], "col": neighbor["col"]} not in destinations:
                                    destinations.append({"row": neighbor["row"], "col": neighbor["col"]})

        # Bottom row is always safe
        for col in range(0, self.skull_finder.col_size):
            self.auto_grid[self.skull_finder.row_size - 1][col]["risk"] = 0
            self.auto_grid[self.skull_finder.row_size - 1][col]["flag"] = False
            if self.skull_finder.grid_displayed_data[self.skull_finder.row_size - 1][col] != globals.CELL_UNEXPLORED:
                return

            if {"row": self.skull_finder.row_size - 1, "col": col} not in destinations:
                destinations.append({"row": self.skull_finder.row_size - 1, "col": col})

        return destinations

    def sum_flagged_neighboring(self, row: int, col: int):
        count = 0
        for x in range(-1, 2):
            if not self.skull_finder.valid_row(row + x):
                continue

            for y in range(-1, 2):
                if not self.skull_finder.valid_col(col + y):
                    continue

                if self.auto_grid[row + x][col + y]["flag"]:
                    count += 1

        return count

    def get_unexplored_nonflagged_neighbors(self, row: int, col: int):
        eligible_cells = []
        for x in range(-1, 2):
            if not self.skull_finder.valid_row(row + x):
                continue

            for y in range(-1, 2):
                if not self.skull_finder.valid_col(col + y):
                    continue

                if (self.skull_finder.grid_displayed_data[row + x][col + y] == globals.CELL_UNEXPLORED and
                        not self.auto_grid[row + x][col + y]["flag"]):
                    eligible_cells.append({"row": row + x, "col": col + y})

        return eligible_cells


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    app.exec()
