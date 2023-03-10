
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import math
import os as _os_module
import queue as _queue_module
import time
import threading

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
        self.mouse_pos = QPoint(0, 0)
        self.rpc_queue = _queue_module.Queue(maxsize=1024)

        self.timer = QTimer()
        self.time = QTime(0, 0, 0)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(10)

    #def keyPressEvent(self, event):
    #    dPrint('key')

    #def mousePressEvent(self, event):
    #    dPrint('mouse')

    def timerEvent(self):
        if self.rpc_queue.empty():
            return
        s = self.rpc_queue.qsize()
        for i in range(s):
            rpc_call = self.rpc_queue.get_nowait()
            rpc_call.call(*rpc_call.args)

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position()


class GameBase():
    def __init__(self, resx, resy, title):
        self.app = QApplication([])
        self.window = GameWindow(resx, resy, title)
        self.window.show()

    def mouse(self):
        return Pair(int(self.window.mouse_pos.x()), int(self.window.mouse_pos.y()))

    def mouse_x(self):
        return int(self.window.mouse_pos.x())

    def mouse_y(self):
        return int(self.window.mouse_pos.y())


class Game():
    def __init__(self, resx=1000, resy=1000, title='scratch game'):
        self.__internal_obj_ref = GameBase(resx, resy, title)

    def mouse(self):
        """
        returns mouse object
        """
        return self.__internal_obj_ref.mouse()

    def mouse_x(self):
        """
        returns mouse (x) coordinate
        """
        return self.__internal_obj_ref.mouse_x()

    def mouse_y(self):
        """
        returns mouse (y) coordianate
        """
        return self.__internal_obj_ref.mouse_y()

    def loop(self):
        """
        start game main loop
        """
        return self.__internal_obj_ref.app.exec()


class RPCcall():
    def __init__(self, call, *args):
        self.call = call
        self.args = args


class Worker(QThread):
    def __init__(self, obj, pixmap, routine, args, kwargs):
        self.pos_x = 0
        self.pos_y = 0
        self.angle = 0
        self.scale = 1.0

        game = args[0]
        self.rpc_queue = game._Game__internal_obj_ref.window.rpc_queue
        self.obj = obj
        self.pixmap = pixmap
        self.routine = routine
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def __del__(self):
        self.wait()

    def rpc_set_pixmap(self, pixmap):
        self.rpc_queue.put(RPCcall(self.obj.setPixmap, pixmap))

    def rpc_set_pos(self, x, y):
        self.rpc_queue.put(RPCcall(self.obj.setPos, x, y))

    def rpc_set_rotation(self, angle):
        self.rpc_queue.put(RPCcall(self.obj.setRotation, angle))

    def rpc_set_scale(self, scale):
        self.rpc_queue.put(RPCcall(self.obj.setScale, scale))

    def set_pos(self, x, y):
        self.pos_x = x
        self.pos_y = y
        self.rpc_set_pos(x - self.pixmap.width() // 2,
                         y - self.pixmap.height() // 2)

    def move(self, x, y):
        self.setpos(self.pos_x + x, self.pos_y + y)

    def set_rotation(self, angle):
        self.angle = angle
        self.rpc_set_rotation(-angle)

    def turn_right(self, angle):
        self.set_rotation(self.angle + angle)

    def turn_left(self, angle):
        self.set_rotation(self.angle - angle)

    def point_to(self, obj):
        angle = math.atan2(obj.get_x() - self.pos_x, obj.get_y() - self.pos_y)
        self.set_rotation(round(angle * 180 / math.pi) - 90)

    def set_scale(self, scale):
        if scale < 0:
            raise ValueError(f'cannot set scale to negative value ({scale})')
        self.scale = scale
        self.rpc_set_scale(scale)

    def resize(self, size):
        if size < 0:
            raise ValueError(f'cannot set size to negative value ({size})')
        self.scale *= size
        self.rpc_set_scale(self.scale)

    def get_scale(self):
        return self.scale

    def set_sprite(self, path):
        if not _os_module.path.exists(path):
            raise ValueError(f'path ({path}) does not exist')
        self.pixmap = QPixmap(path)
        self.rpc_set_pixmap(self.pixmap)
        self.rpc_set_rotation(self.angle)
        self.rpc_set_scale(self.scale)

    def hide(self):
        self.rpc_set_pixmap(QPixmap())

    def show(self):
        self.rpc_set_pixmap(self.pixmap)

    def collide(self, other):
        vert_collide = \
            self.pos_y <= other.get_y() <= self.pos_y + self.pixmap.height() or \
            other.get_y() <= self.pos_y <= other.get_y() + other.get_height()
        hor_collide = \
            self.pos_x <= other.get_x() <= self.pos_x + self.pixmap.width() or \
            other.get_x() <= self.pos_x <= other.get_x() + other.get_width()
        return vert_collide and hor_collide

    def run(self):
        self.routine(*self.args, **self.kwargs)


class SpriteBase(QWidget):

    def __init__(self, routine, path, worker_args, worker_kwargs):
        super().__init__()

        pixmap = QPixmap(path)
        game = worker_args[0]
        scene = game._Game__internal_obj_ref.window.scene
        self.obj = scene.addPixmap(pixmap)
        center = self.obj.boundingRect().center()
        self.obj.setTransformOriginPoint(center)

        self.path = path
        self.worker = Worker(self.obj, pixmap, routine, worker_args, worker_kwargs)

    def __str__(self):
        n = type(self).__name__
        x = self.worker.pos_x
        y = self.worker.pos_y
        return f'{n}(x={x}, y={y})'

    def clone(self, parent, clone_args, clone_kwargs):
        if len(clone_args) == 0 or type(clone_args[0]) != Game:
            raise TypeError('expected (Game) for first argument of clone method')

        cloned_parent = type(parent).__new__(type(parent))
        Sprite.__init__(cloned_parent, cloned_parent.as_clone, self.path, clone_args, clone_kwargs)
        return cloned_parent


def sprite(path):
    def sprite_wrapper(original_class):
        def new_init(self, *args, **kwargs):
            if len(args) == 0 or type(args[0]) != Game:
                raise TypeError('expected (Game) for first argument')
            Sprite.__init__(self, self.run, path, args, kwargs)

        if not _os_module.path.exists(path):
            raise ValueError(f'path ({path}) does not exist')
        original_class.__init__ = new_init
        return original_class
    return sprite_wrapper

def rpc_method(function):
    def wrapper(*args, **kwargs):
        retval = function(*args, **kwargs)
        time.sleep(0.001)
        return retval
    return wrapper

class Sprite():
    def __init__(self, routine, image_path, worker_args, worker_kwargs):
        self.__internal_obj_ref = SpriteBase(routine, image_path, worker_args, worker_kwargs)
        self.__internal_obj_ref.worker.start()

    def __str__(self):
        return self.__internal_obj_ref.__str__()

    @rpc_method
    def set_pos(self, x, y):
        """
        set sprite position to (x, y)
        """
        self.__internal_obj_ref.worker.set_pos(x, y)

    @rpc_method
    def move(self, x, y):
        """
        move to (x, y) shift from current position
        """
        self.__internal_obj_ref.worker.move(x, y)

    @rpc_method
    def set_rotation(self, angle):
        """
        set sprite rotation to (angle) degrees
        """
        self.__internal_obj_ref.worker.set_rotation(angle)

    @rpc_method
    def turn_right(self, angle):
        """
        rotate sprite to (angle) degrees clockwise
        """
        self.__internal_obj_ref.worker.turn_right(angle)

    @rpc_method
    def turn_left(self, angle):
        """
        rotate sprite to (angle) degrees counter clockwise
        """
        self.__internal_obj_ref.worker.turn_left(angle)

    @rpc_method
    def point_to(self, object):
        """
        set sprite rotation to point to (object)
        """
        self.__internal_obj_ref.worker.point_to(object)

    def get_x(self):
        """
        returns sprites (x) coordinate
        """
        return self.__internal_obj_ref.worker.pos_x

    def get_y(self):
        """
        returns sprites (y) coordinate
        """
        return self.__internal_obj_ref.worker.pos_y

    def get_width(self):
        """
        returns sprites (width)
        """
        return self.__internal_obj_ref.worker.pixmap.width()

    def get_height(self):
        """
        returns sprites (height)
        """
        return self.__internal_obj_ref.worker.pixmap.height()

    def get_angle(self):
        """
        return (angle) value in degrees
        """
        return self.__internal_obj_ref.worker.angle

    @rpc_method
    def set_scale(self, scale):
        """
        set sprite (scale) relative to the original (scale)
        """
        self.__internal_obj_ref.worker.set_scale(scale)

    @rpc_method
    def resize(self, size):
        """
        change sprite(scale) relative to the current (scale)
        """
        self.__internal_obj_ref.worker.resize(size)

    def get_scale(self):
        """
        returns sprites (scale)
        """
        return self.__internal_obj_ref.worker.scale

    @rpc_method
    def set_sprite(self, path):
        """
        set sprite image to new one
        """
        self.__internal_obj_ref.worker.set_sprite(path)

    @rpc_method
    def hide(self):
        """
        hide sprite
        """
        self.__internal_obj_ref.worker.hide()

    @rpc_method
    def show(self):
        """
        show sprite
        """
        self.__internal_obj_ref.worker.show()

    def collide(self, other):
        """
        check collision between sprites
        """
        return self.__internal_obj_ref.worker.collide(other)

    def run(self):
        """
        function called when sprite is created
        """
        pass

    @rpc_method
    def clone(self, *args, **kwargs):
        """
        create and return sprite clone
        """
        return self.__internal_obj_ref.clone(self, args, kwargs)

    def as_clone(self, *args, **kwargs):
        """
        function called when sprite is cloned
        """
        pass


@sprite('images/sprite_blue.png')
class BoxArray(Sprite):
    def run(self, game):
        self.hide()
        self.set_pos(200, 200)
        clones = []
        for x in range(1, 10):
            for y in range(1, 10):
                c = self.clone(game)
                c.set_pos(x * 50, y * 50)
                c.resize(0.5)
                clones.append(c)

        for c in clones:
            c.set_sprite('images/sprite_yellow.png')

        for c in clones:
            c.hide()

        for c in clones:
            c.show()

    def as_clone(self, game):
        print('b1 clone')
        while True:
            self.point_to(b2)

@sprite('images/sprite_green.png')
class BoxCollide(Sprite):
    def run(self, game, x, y):
        self.set_pos(x, y)
        #self.set_rotation(45)
        while True:
            if self.collide(b2):
                self.set_sprite('images/sprite_red.png')
            else:
                self.set_sprite('images/sprite_green.png')

@sprite('images/sprite_yellow.png')
class Box2(Sprite):
    def run(self, game):
        while True:
            self.set_pos(game.mouse_x(), game.mouse_y())

    def as_clone(self, game):
        print('b2 clone')


if __name__ == '__main__':
    game = Game()

    a = BoxArray(game)

    bc = BoxCollide(game, 700, 700)
    b2 = Box2(game)


    game.loop()

