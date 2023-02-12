
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import math
import os
import time
from abc import abstractmethod

def dPrint(*args):
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

    def keyPressEvent(self, event):
        dPrint('key')

    def mousePressEvent(self, event):
        dPrint('mouse')

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position()


class GameBase():

    def __init__(self, resx, resy, title):
        self.__app = QApplication([])
        self.__window = GameWindow(resx, resy, title)
        self.__window.show()

    def __method_mouse(self):
        return Pair(self.__window.mouse_pos.x(), self.__window.mouse_pos.y())

    def __method_loop(self):
        self.__app.exec()

    def __method_mouse_x(self):
        return self.__window.mouse_pos.x()

    def __method_mouse_y(self):
        return self.__window.mouse_pos.y()


class Game(GameBase):
    def __init__(self, resx=1000, resy=1000, title='scratch game'):
        super().__init__(resx, resy, title)

    def mouse(self):
        """
        returns mouse object
        """
        return self._GameBase__method_mouse()

    def mouse_x(self):
        """
        returns mouse (x) coordinate
        """
        return self._GameBase__method_mouse_x()

    def mouse_y(self):
        """
        returns mouse (y) coordianate
        """
        return self._GameBase__method_mouse_y()

    def loop(self):
        """
        start game main loop
        """
        return self._GameBase__method_loop()


class Worker(QThread):

    sig_set_pixmap = pyqtSignal(QPixmap)
    sig_set_pos = pyqtSignal(Pair)
    sig_set_rotation = pyqtSignal(int)

    def __init__(self, pixmap, routine, args, kwargs):
        self.x = 0
        self.y = 0
        self.angle = 0

        self.orig = pixmap
        self.pixmap = pixmap.copy()
        self.routine = routine
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def setpos(self, x, y):
        self.x = x
        self.y = y
        self.sig_set_pos.emit(Pair(x - self.pixmap.width() // 2,
                                   y - self.pixmap.height() // 2))

    def move(self, x, y):
        self.setpos(self.x + x, self.y + y)

    def setrotation(self, angle):
        self.angle = angle
        self.sig_set_rotation.emit(-angle)

    def right(self, angle):
        self.setrotation(self.angle + angle)

    def left(self, angle):
        self.setrotation(self.angle - angle)

    def point_to(self, obj):
        angle = math.atan2(obj.get_x() - self.y, obj.get_y() - self.x)
        self.setrotation(round(angle * 180 / math.pi) - 90)

    def run(self):
        self.routine(*self.args, **self.kwargs)


class SpriteBase(QWidget):

    @pyqtSlot(Pair)
    def __slot_set_pos(self, coords):
        self.__obj.setPos(coords.x, coords.y)

    @pyqtSlot(int)
    def __slot_set_rotation(self, angle):
        self.__obj.setRotation(angle)

    @pyqtSlot(QPixmap)
    def __slot_set_pixmap(self, pixmap):
        self.__obj.setPixmap(pixmap)

    def __init__(self, path, args, kwargs):
        super().__init__()
        if not os.path.exists(path):
            raise ValueError(f'path ({path}) does not exist')
        game = args[0]
        self.__scene = game._GameBase__window.scene

        pixmap = QPixmap(path)
        self.__obj = self.__scene.addPixmap(pixmap)
        center = self.__obj.boundingRect().center()
        self.__obj.setTransformOriginPoint(center)

        self.__worker = Worker(pixmap, self.run, args, kwargs)
        self.__worker.sig_set_pos.connect(self.__slot_set_pos)
        self.__worker.sig_set_rotation.connect(self.__slot_set_rotation)
        self.__worker.sig_set_pixmap.connect(self.__slot_set_pixmap)
        self.__worker.start()

    def __str__(self):
        n = type(self).__name__
        x = self.__worker.x
        y = self.__worker.y
        return f'{n}(x={x}, y={y})'

    def __internal_delay(self):
        time.sleep(0.01)

    def __method_setpos(self, x, y):
        self.__worker.setpos(x, y)
        self.__internal_delay()

    def __method_setrotation(self, angle):
        self.__worker.setrotation(angle)
        self.__internal_delay()

    def __method_right(self, angle):
        self.__worker.right(angle)
        self.__internal_delay()

    def __method_left(self, angle):
        self.__worker.left(angle)
        self.__internal_delay()

    def __method_point_to(self, obj):
        self.__worker.point_to(obj)
        self.__internal_delay()

    def __method_get_x(self):
        return self.__worker.x

    def __method_get_y(self):
        return self.__worker.y

    def __method_clone(self, args):
        pass


class Sprite(SpriteBase):
    def __init__(self, *args):
        super().__init__(*args)

    def setpos(self, x, y):
        """
        set sprite position to (x, y)
        """
        self._SpriteBase__method_setpos(x, y)

    def setrotation(self, angle):
        """
        set sprite rotation to (angle) degrees
        """
        self._SpriteBase__method_setrotation(angle)

    def right(self, angle):
        """
        rotate sprite to (angle) degrees clockwise
        """
        self._SpriteBase__method_right(angle)

    def left(self, angle):
        """
        rotate sprite to (angle) degrees counter clockwise
        """
        self._SpriteBase__method_left(angle)

    def point_to(self, object):
        """
        set sprite rotation to point to (object)
        """
        self._SpriteBase__method_point_to(object)

    def get_x(self):
        """
        returns sprites (x) coordinate
        """
        return self._SpriteBase__method_get_x()

    def get_y(self):
        """
        returns sprites (y) coordinate
        """
        return self._SpriteBase__method_get_y()

    def run(self):
        """
        function called when sprite is created
        """
        pass

    def clone(self, *args):
        """
        create sprite clone
        """
        self._SpriteBase__method_clone(args)

    def as_clone(self, *args):
        """
        function called when sprite is cloned
        """
        pass


def sprite(path):
    def sprite_wrapper(original_class):
        def new_init(self, *args, **kwargs):
            if len(args) == 0 or type(args[0]) != Game:
                raise TypeError('expected (Game) for first argument')
            Sprite.__init__(self, path, args, kwargs)

        original_class.__init__ = new_init
        return original_class
    return sprite_wrapper


@sprite('images/sprite.png')
class Box(Sprite):
    def run(self, game):
        self.setpos(200, 200)
        while True:
            self.point_to(b2)


@sprite('images/sprite2.png')
class Box2(Sprite):
    def run(self, game, arg):
        print(arg)
        while True:
            self.setpos(game.mouse_x(), game.mouse_y())


if __name__ == '__main__':
    g = Game()

    b1 = Box(g)
    b2 = Box2(g, 'lol')

    #b1 = Box(g)
    #b2 = Box(g)

    g.loop()

