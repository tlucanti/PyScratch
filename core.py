
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import math
import os
import time

def dPrint(*args):
    print(*args)

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

    def sigAdd():
        pass


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

    sigAddPixmap = pyqtSignal(int)

    def __init__(self, game, path):
        super().__init__()

        self.x = 0
        self.y = 0
        self.angle = 0

        self.orig = QPixmap(path)
        self.pixmap = QPixmap(path)
        self.diag = int(math.hypot(self.pixmap.width(), self.pixmap.height()))
        dPrint('emmiting signal: addPixmap', self.pixmap)
        #self.sigAddPixmap.emit(self.pixmap)
        #self.setpos(0, 0)


    def __del__(self):
        self.wait()

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
        self.sigAddPixmap.emit(123)
        pass

class Sprite(QWidget):

    @pyqtSlot(int)
    def __slotAddPixmap(self, pixmap):
        dPrint('got signal: adding pixmap', pixmap)
        #self.__game.__window.scene.addPixmap(pixmap)

    def __init__(self, game, path):
        super().__init__()
        if not os.path.exists(path):
            raise ValueError(f'path ({path}) does not exist')
        self.__game = game
        self.__worker = Worker(game, path)
        self.__worker.sigAddPixmap.connect(self.__slotAddPixmap)
        self.__worker.start()


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
    #b1 = Box(g)
    #b2 = Box(g)

    g.loop()

