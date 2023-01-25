
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import math
import os
import time

class GameWindow(QGraphicsView):
    def __init__(self, resx, resy, title):
        super().__init__()
        self.setFixedSize(resx, resy)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(2, 2, resx - 2, resy - 2)
        self.setScene(self.scene)
        self.setMouseTracking(True)
        self.mouse_pos = QPointF(0, 0)

    def keyPressEvent(self, e):
        print('key')

    def mousePressEvent(self, e):
        print('mouse')

    def mouseMoveEvent(self, e):
        self.mouse_posi = e.position()


class Game():
    def __init__(self, resx=1000, resy=800, title='scratch game'):
        self._app = QApplication([])
        self._window = _GameWindow(resx, resy, title)
        self._window.show()

    def mouse_x(self):
        return self._window.mouse_pos.x()

    def mouse_y(self):
        return self._window.mouse_pos.y()

    def loop(self):
        self._app.exec()


class Worker(QThread):
    def __init__(self):

class Sprite(QThread):
    def __init__(self, game, path):
        super().__init__()
        self._x = 0
        self._y = 0
        self._angle = 0

        if not os.path.exists(path):
            raise ValueError(f'path ({path}) does not exist')
        self._orig = QPixmap(path)
        self._pixmap = QPixmap(path)
        self._diag = int(math.hypot(self._pixmap.width(), self._pixmap.height()))
        self._obj = game._window.scene.addPixmap(self._pixmap)
        self.setpos(0, 0)

    def setpos(self, x, y):
        self._x = x
        self._y = y
        self._obj.setOffset(x - self._diag / 2, y - self._diag / 2)

    def move(self, x, y):
        self.setpos(self._x + x, self._y + y)

    def setangle(self, angle):
        self._angle = angle
        transform = QTransform()
        transform.translate(self._orig.width() / 2, self._orig.height() / 2)
        transform.rotate(self._angle)
        transform.translate(-self._orig.width() / 2, -self._orig.height() / 2)
        self._pixmap = self._orig.transformed(transform)
        self._label.setPixmap(self._pixmap)

    def right(self, angle):
        self.setangle(self._angle + angle)

    def left(self, angle):
        self.setangle(self._angle - angle)

    def point_to(self, x, y):
        angle = math.atan2(y - self._y, x - self._x)
        self.setangle(angle * 180 / math.pi)

    def run(self):
        pass


class Box(Sprite):
    def __init__(self, game):
        self.game = game
        super().__init__(game, 'images/sprite.png')

    def run(self):
        self.setpos(200, 200)
        return
        for i in range(100):
            self.setpos(i, i)
            time.sleep(0.05)


if __name__ == '__main__':
    g = Game()

    b1 = Box(g)
    b1.start()
    #b1 = Box(g)
    #b2 = Box(g)

    g.loop()

