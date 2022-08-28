# Kivy Main Auto Template
from math import sqrt
from random import randint
from configuration import WINDOW_WIDTH, WINDOW_HEIGHT
from kivy.config import Config
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.utils import get_random_color
from kivy.graphics import Ellipse, Color
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.core.window import Window
from kivy.clock import Clock

Config.set("graphics", "width", WINDOW_WIDTH)
Config.set("graphics", "height", WINDOW_HEIGHT)
Config.set("graphics", "resizable", False)
Config.write()


class Circle(Widget):
    x_velocity = NumericProperty(0)
    y_velocity = NumericProperty(0)
    velocity = ReferenceListProperty(x_velocity, y_velocity)

    def __init__(self, rad=100, x=0, y=0, moveable=False, **kwargs):
        super().__init__(**kwargs)
        self.moveable = moveable
        self.x, self.y = x, y
        self.rad = rad
        self.grab_x, self.grab_y = None, None
        with self.canvas:
            Color(rgb=get_random_color(1))
            self.circle = Ellipse()
            self.circle.pos = self.pos
            self.circle.size = rad*2, rad*2
        self.bind(pos=self.set_circle_pos)

    def set_circle_pos(self, *_):
        self.circle.pos = self.pos

    def circle_collide_point(self, x, y):
        distx = x - (self.x + self.rad)
        disty = y - (self.y + self.rad)
        distance = sqrt((distx*distx) + (disty*disty))
        if distance <= self.rad:
            return True
        return False

    def circle_collide_circle(self, circle1, push=2):
        distx = (circle1.x + circle1.rad) - (self.x + self.rad)
        disty = (circle1.y + circle1.rad) - (self.y + self.rad)
        distance = sqrt((distx*distx) + (disty*disty))
        overlap = (distance - (self.rad + circle1.rad)) * 0.5
        if distance <= (self.rad + circle1.rad):
            if push >= 1:
                self.x -= overlap * (self.x - circle1.x) / distance
                self.y -= overlap * (self.y - circle1.y) / distance
                if push >= 2:
                    circle1.x += overlap * (self.x - circle1.x) / distance
                    circle1.y += overlap * (self.y - circle1.y) / distance
            return True
        return False

    def on_touch_down(self, touch):
        if self.circle_collide_point(*touch.pos) and self.moveable:
            self.grab_x = self.x - touch.x
            self.grab_y = self.y - touch.y
            touch.grab(self)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self.moveable:
            self.x = touch.x + self.grab_x
            self.y = touch.y + self.grab_y
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self and self.moveable:
            touch.ungrab(self)
            self.grab_x = None
            self.grab_y = None
        return super().on_touch_up(touch)


class GameWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = Window.size
        self.circle_grab = None
        self.grab_x = None
        self.grab_y = None
        self.all_widget()
        self.main_circle()
        self.setup_window()
        self.start_loop()

    def all_widget(self):
        self.all_circle = Widget()
        self.add_widget(self.all_circle)

    def start_loop(self):
        self.start_clock = Clock.schedule_interval(
            lambda _: self.game_loop(), 1.0/60.0)

    def game_loop(self):
        self.check_key()
        for circle1 in self.all_circle.children:
            for circle2 in self.all_circle.children:
                if circle1 != circle2:
                    circle2.circle_collide_circle(circle1)
                    self.circle.circle_collide_circle(circle2, 2)

    def all_key_move(self):
        self.move_up = False
        self.move_down = False
        self.move_right = False
        self.move_left = False

    def setup_window(self):
        self.all_key_move()
        self._keyboard = Window.request_keyboard(self._keyboard_close, self)
        self._keyboard.bind(on_key_down=self._keyboard_down_key)
        self._keyboard.bind(on_key_up=self._keyboard_up_key)

    def _keyboard_close(self):
        self._keyboard.unbind(on_key_down=self._keyboard_down_key)
        self._keyboard.unbind(on_key_up=self._keyboard_up_key)
        self._keyboard = None

    def _keyboard_down_key(self, _, key, *__):
        if key[1] == "w":
            self.move_up = True
            self.move_down = False
        elif key[1] == "s":
            self.move_down = True
            self.move_up = False
        elif key[1] == "a":
            self.move_left = True
            self.move_right = False
        elif key[1] == "d":
            self.move_right = True
            self.move_left = False

    def _keyboard_up_key(self, _, key, *__):
        if key[1] == "w":
            self.move_up = False
        elif key[1] == "s":
            self.move_down = False
        elif key[1] == "a":
            self.move_left = False
        elif key[1] == "d":
            self.move_right = False

    def check_key(self):
        adder = 5
        if self.move_up and self.move_down is False:
            self.circle.y += adder
        elif self.move_down and self.move_up is False:
            self.circle.y -= adder
        if self.move_right and self.move_left is False:
            self.circle.x += adder
        elif self.move_left and self.move_right is False:
            self.circle.x -= adder

    def main_circle(self):
        self.circle = Circle(rad=50, x=self.center_x-50, y=self.center_y-50)
        self.add_widget(self.circle)
        for _ in range(10):
            self.add_circle(randint(0, Window.width), randint(
                0, Window.height), randint(50, 100))

    def add_circle(self, x, y, rad=50):
        radius = rad
        circle = Circle(rad=radius, x=x, y=y)
        self.all_circle.add_widget(circle)


class GameApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "GameApp"

    def get_game_widget(self):
        self.game_screen = Screen()
        self.game_widget = GameWidget()
        self.game_screen.add_widget(self.game_widget)
        self.sm.add_widget(self.game_screen)

    def build(self):
        self.sm = ScreenManager()
        self.get_game_widget()
        return self.sm


if __name__ == "__main__":
    GameApp().run()
