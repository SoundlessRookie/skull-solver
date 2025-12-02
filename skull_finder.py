"""skull_finder.py

Classic Defaults:
- Grid size: 7 x 7
- Mine count: (x-axis * y-axis / 8) + 1
  - For 7x7 grid: (7 * 7 / 8) + 1 = 8
- No mines on the bottom row
- Valid mine placements:
  - Must not already have a mine in the cell
  - No more than 2 mines neighboring the cell
  - Less than 1/3 of the total mines in the same row

Grindworks Defaults:
- TODO
"""
import random


class SkullFinder:
    CELL_EXPLORED_BLANK = 0
    CELL_UNEXPLORED = -1
    CELL_EXPLORED_SKULL = -2

    PLAYING = 0
    WIN = 1
    LOSE = 2

    TOP_ROW = 0
    OFFSET_SAFE_ROW = 1
    MAX_ITERATIONS = 1000

    def __init__(self, row_size: int = 7, col_size: int = 7):
        self.row_size: int = row_size
        self.col_size: int = col_size
        self.skull_count: int = (row_size * col_size) // 8 + 1
        self.status: int = self.PLAYING

        self.grid_skull_data = []
        for _ in range(self.row_size):
            self.grid_skull_data.append([False] * self.col_size)

        self.grid_displayed_data = []
        for _ in range(self.row_size):
            self.grid_displayed_data.append([self.CELL_UNEXPLORED] * self.col_size)

    def fill_grid(self):
        placed_skulls = 0
        max_iterations = self.MAX_ITERATIONS

        if self.skull_count < 0:
            raise ValueError("Skull count cannot be negative.")

        while placed_skulls < self.skull_count:
            if max_iterations <= 0:
                raise RuntimeError(
                    f"Max iterations reached while placing skulls: {placed_skulls} out of {self.skull_count}.")
            max_iterations -= 1

            row = random.randint(0, self.row_size - (1 + self.OFFSET_SAFE_ROW))
            col = random.randint(0, self.col_size - 1)

            # Check conditions for placing a skull at the selected location
            if (not self.is_skull(row, col) and
                    self.sum_neighboring_skulls(row, col) < 2 and
                    self.sum_row_skulls(row) < self.skull_count):
                self.place_skull(row, col)
                placed_skulls += 1

    def explore_cell(self, row: int, col: int, game_over: bool = False):
        if self.grid_displayed_data[row][col] != self.CELL_UNEXPLORED:
            return

        if self.is_skull(row, col):
            self.grid_displayed_data[row][col] = self.CELL_EXPLORED_SKULL

            if not game_over:
                self.lose()
        else:
            self.grid_displayed_data[row][col] = self.sum_neighboring_skulls(row, col)

            if row == self.TOP_ROW and not game_over:
                self.win()

            # Reveal all neighboring cells if the current cell is blank
            if self.grid_displayed_data[row][col] == self.CELL_EXPLORED_BLANK:
                for x in range(-1, 2):
                    if not self.valid_row(row + x):
                        continue

                    for y in range(-1, 2):
                        if not self.valid_col(col + y):
                            continue

                        self.explore_cell(row + x, col + y, game_over=game_over)

    def sum_neighboring_skulls(self, row: int, col: int):
        count = 0
        for x in range(-1, 2):
            if not self.valid_row(row + x):
                continue

            for y in range(-1, 2):
                if not self.valid_col(col + y):
                    continue

                if self.is_skull(row + x, col + y):
                    count += 1

        return count

    def sum_row_skulls(self, row: int):
        count = 0
        for col in range(self.col_size):
            if self.is_skull(row, col):
                count += 1

        return count

    def valid_row(self, row: int):
        if row < 0 or row >= self.row_size:
            return False
        return True

    def valid_col(self, col: int):
        if col < 0 or col >= self.col_size:
            return False
        return True

    def print_skull_grid(self):
        for row in self.grid_skull_data:
            print(row)

    def print_displayed_grid(self):
        for row in self.grid_displayed_data:
            print(row)

    def win(self):
        self.status = self.WIN

    def lose(self):
        self.status = self.LOSE

    def reveal_all(self):
        for row in range(self.row_size):
            for col in range(self.col_size):
                self.explore_cell(row, col, game_over=True)

    def is_skull(self, row: int, col: int):
        return self.grid_skull_data[row][col]

    def place_skull(self, row: int, col: int):
        self.grid_skull_data[row][col] = True


if __name__ == "__main__":
    skull_finder = SkullFinder()
    skull_finder.fill_grid()

    print("\nSkull Grid")
    skull_finder.print_skull_grid()

    print("\nDisplayed Grid")
    skull_finder.print_displayed_grid()

    while True:
        print("\nEnter \"exit\" to exit. Rows and columns start at 0.")

        try:
            input_row = int(input("Enter row: "))
        except ValueError:
            print("Invalid row.")
            continue

        if input_row == "exit":
            break
        if not skull_finder.valid_row(input_row):
            print("Invalid row.")
            continue

        try:
            input_col = int(input("Enter column: "))
        except ValueError:
            print("Invalid column.")
            continue

        if input_col == "exit":
            break
        if not skull_finder.valid_col(input_col):
            print("Invalid column.")
            continue

        skull_finder.explore_cell(input_row, input_col)

        print("\nDisplayed Grid")
        skull_finder.print_displayed_grid()

        if skull_finder.status == skull_finder.WIN:
            print("\nYou Win!")
            skull_finder.reveal_all()

            print("\nDisplayed Grid")
            skull_finder.print_displayed_grid()
            break

        elif skull_finder.status == skull_finder.LOSE:
            print("\nYou Lose!")
            skull_finder.reveal_all()

            print("\nDisplayed Grid")
            skull_finder.print_displayed_grid()
            break
