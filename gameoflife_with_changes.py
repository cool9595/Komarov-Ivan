import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor
import json

# Конфигурация из json
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

class GameOfLife:
    def __init__(self, rows, cols, ruleset="classic"):
        self.rows = rows
        self.cols = cols
        self.grid = self.create_grid(False)
        self.ruleset = ruleset
        self.shapes = self.load_shapes()

    def create_grid(self, randomize=True):
        from random import choice
        grid = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        if randomize:
            for r in range(self.rows):
                for c in range(self.cols):
                    grid[r][c] = choice([False, True, False, False])
        return grid

    def load_shapes(self):
        return {
            "glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
            "small_exploder": [(1, 0), (0, 1), (1, 1), (2, 1), (0, 2), (2, 2), (1, 3)],
        }

    def get_neighbor_count(self, r, c):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.cols
                if self.grid[nr][nc]:
                    count += 1
        return count

    def update(self):
        new_grid = self.create_grid(False)
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self.get_neighbor_count(r, c)
                alive = self.grid[r][c]
                if self.ruleset == "classic":
                    if alive and neighbors in [2, 3]:
                        new_grid[r][c] = True
                    elif not alive and neighbors == 3:
                        new_grid[r][c] = True
                elif self.ruleset == "alternative":
                    if alive and neighbors in [2, 3]:
                        new_grid[r][c] = True
                    elif not alive and neighbors in [3, 6]:
                        new_grid[r][c] = True
        self.grid = new_grid

    def add_shape(self, shape_name, top_left_r, top_left_c):
        shape = self.shapes.get(shape_name)
        if not shape:
            return
        for dr, dc in shape:
            r = (top_left_r + dr) % self.rows
            c = (top_left_c + dc) % self.cols
            self.grid[r][c] = True

    def clear(self):
        self.grid = self.create_grid(False)

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Игра жизни (89) на PyQt5")
        self.resize(config["window_width"], config["window_height"])

        self.cell_size = config["cell_size"]
        self.rows = config["window_height"] // self.cell_size
        self.cols = config["window_width"] // self.cell_size

        self.game = GameOfLife(self.rows, self.cols)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.animation_speed = config["animation_speed"]
        self.timer.start(self.animation_speed)
        self.dragging_shape = None
        self.mouse_pos = None
        self.selected_shape = "small_exploder"

        self.ruleset = "classic"

    def paintEvent(self, event):
        painter = QPainter(self)
        bg = QColor(*config["background_color"])
        painter.fillRect(self.rect(), bg)

        # Отрисовка сетки
        grid_color = QColor(*config["grid_color"])
        for x in range(0, self.width(), self.cell_size):
            painter.setPen(grid_color)
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), self.cell_size):
            painter.drawLine(0, y, self.width(), y)

        # Отрисовка живых клеток
        alive_color = QColor(*config["alive_color"])
        painter.setBrush(alive_color)
        painter.setPen(Qt.NoPen)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.game.grid[r][c]:
                    rect = QRect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                    painter.drawRect(rect)

        # Отрисовка перетаскиваемой фигуры
        if self.dragging_shape and self.mouse_pos:
            shape_coords = self.game.shapes[self.dragging_shape]
            painter.setBrush(QColor(200, 200, 200, 180))
            for dr, dc in shape_coords:
                x = self.mouse_pos.x() + dc * self.cell_size
                y = self.mouse_pos.y() + dr * self.cell_size
                rect = QRect(x, y, self.cell_size, self.cell_size)
                painter.drawRect(rect)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.game.update()
            self.update()
        elif event.key() == Qt.Key_C:
            self.game.clear()
            self.update()
        elif event.key() == Qt.Key_1:
            self.ruleset = "classic"
            self.game.ruleset = "classic"
        elif event.key() == Qt.Key_2:
            self.ruleset = "alternative"
            self.game.ruleset = "alternative"
        elif event.key() == Qt.Key_Less:  # клавиша '<'
            self.animation_speed += 50
            self.timer.setInterval(self.animation_speed)
        elif event.key() == Qt.Key_Greater:  # клавиша '>'
            self.animation_speed = max(0, self.animation_speed - 50)
            self.timer.setInterval(self.animation_speed)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging_shape = self.selected_shape
            self.mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging_shape:
            r = event.pos().y() // self.cell_size
            c = event.pos().x() // self.cell_size
            self.game.add_shape(self.dragging_shape, r, c)
            self.dragging_shape = None
            self.mouse_pos = None
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging_shape:
            self.mouse_pos = event.pos()
            self.update()

    def update_game(self):
        # Автообновление по таймеру
        self.game.update()
        self.update()

def main():
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
