
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import math
import os
import time

def dPrint(*args):
    return
    print(*args)


class Pair():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

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
        dPrint('key')

    def mousePressEvent(self, e):
        dPrint('mouse')

    def mouseMoveEvent(self, e):
        self.mouse_pos = e.position()


class Game():

    def __init__(self, resx=1000, resy=800, title='scratch game'):
        self.__app = QApplication([])
        self.__window = GameWindow(resx, resy, title)
        self.__window.show()

    def mouse(self):
        return Pair(self.__window.mouse_pos.x(), self.__window.mouse_pos.y())

    def loop(self):
        self.__app.exec()


class Worker(QThread):

    sigAddPixmap = pyqtSignal(QPixmap)
    sigSetPos = pyqtSignal(Pair)
    sigSetRotation = pyqtSignal(int)
    sigSetPixmap = pyqtSignal(QPixmap)

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
        dPrint(' >> setPos:', x, y)
        self.sigSetPos.emit(Pair(
            x - self.pixmap.width() // 2,
            y - self.pixmap.height() // 2))

    def move(self, x, y):
        self.setpos(self.x + x, self.y + y)

    def setrotation(self, deg):
        self.sigSetRotation.emit(deg)

    def right(self, angle):
        self.setrotation(self._angle + angle)

    def left(self, angle):
        self.setrotation(self._angle - angle)

    def point_to(self, obj):
        angle = math.atan2(obj.get_x() - self.y, obj.get_y() - self.x)
        self.setrotation(round(angle * 180 / math.pi) - 90)

    def run(self):
        dPrint(' >> addPixmap:', self.pixmap)
        self.sigAddPixmap.emit(self.pixmap)
        self.routine()

class Sprite(QWidget):

    @pyqtSlot(QPixmap)
    def __slotAddPixmap(self, pixmap):
        dPrint(' << addPixmap:', pixmap)
        self.__obj = self.__scene.addPixmap(pixmap)
        center = self.__obj.boundingRect().center()
        self.__obj.setTransformOriginPoint(center)

    @pyqtSlot(Pair)
    def __slotSetPos(self, coords):
        dPrint(' << setOffset:', coords)
        self.__obj.setPos(coords.x, coords.y)

    @pyqtSlot(int)
    def __slotSetRotation(self, angle):
        dPrint(' << setRotation:', angle)
        self.__obj.setRotation(-angle)

    @pyqtSlot(QPixmap)
    def __slotSetPixmap(self, pixmap):
        dPrint(' << setPixmap:', pixmap)
        self.__obj.setPixmap(pixmap)

    def __init__(self, game, path):
        super().__init__()
        if not os.path.exists(path):
            raise ValueError(f'path ({path}) does not exist')
        self.__scene = game._Game__window.scene

        self.__worker = Worker(game, path, self.run)
        self.__worker.sigAddPixmap.connect(self.__slotAddPixmap)
        self.__worker.sigSetPos.connect(self.__slotSetPos)
        self.__worker.sigSetRotation.connect(self.__slotSetRotation)
        self.__worker.sigSetPixmap.connect(self.__slotSetPixmap)
        self.__worker.start()

    def __delay(self):
        time.sleep(0.01)

    def setpos(self, x, y):
        self.__worker.setpos(x, y)
        self.__delay()

    def setrotation(self, angle):
        self.__worker.setrotation(angle)
        self.__delay()

    def point_to(self, obj):
        self.__worker.point_to(obj)
        self.__delay()

    def run():
        pass


class Box(Sprite):
    def __init__(self, game):
        self.game = game
        super().__init__(game, 'images/sprite.png')

    def run(self):
        self.setpos(200, 200)
        while True:
            self.point_to(self.game.mouse())


class Box2(Sprite):
    def __init__(self, game):
        self.game = game
        super().__init__(game, 'images/sprite2.png')

    def run(self):
        self.setpos(100, 100)
        for i in range(360):
            self.setrotation(i)
            time.sleep(0.01)


if __name__ == '__main__':
    g = Game()

    b1 = Box(g)
    b2 = Box2(g)
    #b1 = Box(g)
    #b2 = Box(g)

    g.loop()

