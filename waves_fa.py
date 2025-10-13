import sys, math, json, os 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QTimer

# метрики по умолчанию
WIDTH, HEIGHT, FPS = 1000, 600, 60
FLOAT_X, FLOAT_RADIUS = 500, 15

# загрузка начальных состояний 
FILE = 'waves.json'
if not os.path.exists(FILE):
    WAVES = [
        {"amplitude": 50, "wavelength": 200, "speed": 100},
        {"amplitude": 40, "wavelength": 150, "speed": 100},
        {"amplitude": 30, "wavelength": 100, "speed": 100},
        {"amplitude": 60, "wavelength": 300, "speed": 100},
    ]
    with open(FILE, 'w') as f:
        json.dump({"waves": WAVES}, f)
else:
    with open(FILE, 'r') as f:
        WAVES = json.load(f)["waves"]

# мейн код 
class WaveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("волны")
        self.setFixedSize(WIDTH, HEIGHT)
        self.time = 0
        QTimer(self, timeout=self.update, interval=1000 // FPS).start()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(0, 0, WIDTH, HEIGHT, Qt.white)
        qp.setRenderHint(QPainter.Antialiasing)
        spacing = HEIGHT // (len(WAVES) + 1)

        for i, w in enumerate(WAVES):
            base_y = spacing * (i + 1)
            A, L, v = w["amplitude"], w["wavelength"], w["speed"]
            k, omega = 2 * math.pi / L, 2 * math.pi * v / L

            qp.setPen(QPen(Qt.red, 2))
            prev_x, prev_y = 0, base_y
            for x in range(0, WIDTH, 4):
                y = base_y + A * math.sin(k * x - omega * self.time) # считаем где будет волна по y на опред x исп угловую частоту
                qp.drawLine(prev_x, prev_y, x, int(y))
                prev_x, prev_y = x, int(y)

            y_float = base_y + A * math.sin(k * FLOAT_X - omega * self.time)
            qp.setBrush(QBrush(Qt.blue))
            qp.setPen(Qt.NoPen)
            qp.drawEllipse(int(FLOAT_X - FLOAT_RADIUS), int(y_float - FLOAT_RADIUS), 2 * FLOAT_RADIUS, 2 * FLOAT_RADIUS)
        self.time += 1 / FPS


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = WaveWidget()
    w.show()

    sys.exit(app.exec_())

