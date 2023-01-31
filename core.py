
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import math
import os
import time

def dPrint(*args):
    print(*args)


class Pair():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def __str__(self):
        return self.__repr__()


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
        self.__app = QApplication([])
        self.__window = GameWindow(resx, resy, title)
        self.__window.show()

    def mouse_x(self):
        return self.__window.mouse_pos.x()

    def mouse_y(self):
        return self.__window.mouse_pos.y()

    def loop(self):
        self.__app.exec()


class Worker(QThread):

    sigAddPixmap = pyqtSignal(QPixmap)
    sigSetOffset = pyqtSignal(Pair)

    def __init__(self, game, path, routine):
        super().__init__()

        self.x = 0
        self.y = 0
        self.angle = 0

        self.game = game
        self.orig = QPixmap(path)
        self.pixmap = QPixmap(path)
        self.diag = int(math.hypot(self.pixmap.width(), self.pixmap.height()))
        self.routine = routine

    def __del__(self):
        self.wait()

    def setpos(self, x, y):
        self.x = x
        self.y = y
        self.sigSetOffset.emit(Pair(x - self.diag / 2, y - self.diag / 2))

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
        #dPrint('emmiting signal: addPixmap', self.pixmap)
        self.sigAddPixmap.emit(self.pixmap)
        self.routine()

class Sprite(QWidget):

    @pyqtSlot(QPixmap)
    def __slotAddPixmap(self, pixmap):
        dPrint('got signal: adding pixmap', pixmap)
        self.__obj = self.__scene.addPixmap(pixmap)

    @pyqtSlot(Pair)
    def __slotSetOffset(self, coords):
        dPrint('got signal: changing coordinates', coords)
        self.__obj.setOffset(coords.x, coords.x)

    def __init__(self, game, path):
        super().__init__()
        if not os.path.exists(path):
            raise ValueError(f'path ({path}) does not exist')
        self.__scene = game._Game__window.scene
        self.__worker = Worker(game, path, self.run)
        self.__worker.sigAddPixmap.connect(self.__slotAddPixmap)
        self.__worker.sigSetOffset.connect(self.__slotSetOffset)
        self.__worker.start()

    def setpos(self, x, y):
        self.__worker.setpos(x, y)


class Box(Sprite):
    def __init__(self, game):
        self.game = game
        super().__init__(game, 'images/sprite.png')

    def run(self):
        self.setpos(200, 200)
        for i in range(100):
            self.setpos(i, i)
            time.sleep(0.05)


if __name__ == '__main__':
    g = Game()

    b1 = Box(g)
    #b1 = Box(g)
    #b2 = Box(g)

    g.loop()

