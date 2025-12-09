import sys
import random
import json
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QMessageBox
from PyQt5.QtCore import QSize, QTimer

class Cell(QPushButton):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.is_mine = False
        self.adjacent_mines = 0
        self.is_revealed = False
        self.setFixedSize(QSize(30, 30))

class Minesweeper(QWidget):
    def __init__(self, rows=10, cols=10, mines=10):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.cells = {}
        self.time_elapsed = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTimer)

        self.initUI()
        self.placeMines()
        self.calculateAdjacents()
        self.timer.start(1000)  # таймер срабатывает каждую секунду

    def initUI(self):
        self.setWindowTitle('Сапёр на PyQt5 — Время: 0 сек')
        for x in range(self.rows):
            for y in range(self.cols):
                cell = Cell(x, y)
                cell.clicked.connect(self.cellClicked)
                self.grid.addWidget(cell, x, y)
                self.cells[(x, y)] = cell
        self.show()

    def updateTimer(self):
        self.time_elapsed += 1
        self.setWindowTitle(f'Сапёр на PyQt5 — Время: {self.time_elapsed} сек')

    def placeMines(self):
        mines_placed = 0
        while mines_placed < self.mines:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)
            cell = self.cells[(x, y)]
            if not cell.is_mine:
                cell.is_mine = True
                mines_placed += 1

    def calculateAdjacents(self):
        for x in range(self.rows):
            for y in range(self.cols):
                cell = self.cells[(x, y)]
                if cell.is_mine:
                    continue
                mines_count = 0
                for nx in range(max(0, x-1), min(self.rows, x+2)):
                    for ny in range(max(0, y-1), min(self.cols, y+2)):
                        if self.cells[(nx, ny)].is_mine:
                            mines_count += 1
                cell.adjacent_mines = mines_count

    def cellClicked(self):
        cell = self.sender()
        if cell.is_revealed:
            return
        if cell.is_mine:
            cell.setText('*')
            cell.setStyleSheet('color: red; background-color: pink;')
            self.gameOver(False)
        else:
            self.revealCell(cell)
            if self.checkWin():
                self.gameOver(True)

    def revealCell(self, cell):
        if cell.is_revealed:
            return
        cell.is_revealed = True
        if cell.adjacent_mines > 0:
            cell.setText(str(cell.adjacent_mines))
        else:
            cell.setText('')
            for nx in range(max(0, cell.x-1), min(self.rows, cell.x+2)):
                for ny in range(max(0, cell.y-1), min(self.cols, cell.y+2)):
                    neighbor = self.cells[(nx, ny)]
                    if not neighbor.is_revealed and not neighbor.is_mine:
                        self.revealCell(neighbor)
        cell.setEnabled(False)

    def gameOver(self, won):
        self.timer.stop()
        msg = QMessageBox()
        if won:
            msg.setText(f'Поздравляем! Вы выиграли за {self.time_elapsed} сек!')
        else:
            msg.setText('Игра окончена! Вы наступили на мину.')
            for cell in self.cells.values():
                if cell.is_mine:
                    cell.setText('*')
                    cell.setStyleSheet('color: black; background-color: red;')
        msg.exec_()
        self.close()

    def checkWin(self):
        for cell in self.cells.values():
            if not cell.is_mine and not cell.is_revealed:
                return False
        return True

if __name__ == '__main__':
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    app = QApplication(sys.argv)
    game = Minesweeper(rows=config.get('rows', 10), cols=config.get('cols', 10), mines=config.get('mines', 10))
    sys.exit(app.exec_())
