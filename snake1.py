from kivy.config import Config
from kivy.app import App
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line, PushMatrix, PopMatrix, Rotate
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from random import randint


GRID_ROWS = 20
GRID_COLS = 20
INITIAL_LENGTH = 3
STORE = JsonStore('highscore.json')

Config.set("graphics", "resizable", "0")
Config.set("graphics", "height", "800")
Config.set("graphics", "width", "800")
Config.write()

class GameField(Widget):
    def __init__(self, score_label, high_score_label, **kwargs):
        super(GameField, self).__init__(**kwargs)
        self.cell_width = self.width // GRID_COLS
        self.cell_height = self.height // GRID_ROWS
        self.direction = (self.cell_width, 0)
        self.next_direction = self.direction
        self.snake = self.initialize_snake()
        self.food = self.random_position()
        self.score = 0
        self.score_label = score_label
        self.high_score_label = high_score_label
        self.high_score = STORE.get('high_score')['score'] if STORE.exists('high_score') else 0
        self.high_score_label.text = f"High Score: {self.high_score}"
        Clock.schedule_interval(self.update, 0.1)
        self.bind(size=self.adjust_grid, pos=self.adjust_grid)

    def initialize_snake(self):
        start_x = self.cell_width * 3
        start_y = self.cell_height * 3
        return [(start_x - i * self.cell_width, start_y) for i in range(INITIAL_LENGTH)]

    def adjust_grid(self, *args):
        self.cell_width = self.width // GRID_COLS
        self.cell_height = self.height // GRID_ROWS
        self.reset_game()

    def update(self, *args):
        if (self.next_direction[0] != -self.direction[0] or
            self.next_direction[1] != -self.direction[1]):
            self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        if (new_head in self.snake or
                not (0 <= new_head[0] < self.width) or
                not (0 <= new_head[1] < self.height)):
            if self.score > self.high_score:
                self.high_score = self.score
                STORE.put('high_score', score=self.high_score)
            self.reset_game()
            return

        if new_head == self.food:
            self.snake.append(self.snake[-1])
            self.food = self.random_position()
            self.update_score(100)

        self.snake = [new_head] + self.snake[:-1]
        self.canvas.clear()
        self.draw_grid()
        self.draw_objects()

    def draw_grid(self):

        with self.canvas.before:
            self.canvas.before.clear()

            Color(0, 0, 0.5, 1)
            Rectangle(pos=self.pos, size=self.size)


            Color(0, 0.5, 0, 1)
            for row in range(GRID_ROWS + 1):
                y = self.pos[1] + row * self.cell_height
                Line(points=[self.pos[0], y, self.pos[0] + self.width, y], width=1)
            for col in range(GRID_COLS + 1):
                x = self.pos[0] + col * self.cell_width
                Line(points=[x, self.pos[1], x, self.pos[1] + self.height], width=1)

    def draw_objects(self):

        with self.canvas:
            Color(1,1,1,1)
            for i, segment in enumerate(self.snake):
                texture = Image("head_snake4.png" if i == 0 else "body_snake4.png").texture
                texture.wrap = "clamp_to_edge"
                x, y = segment
                direction = self.direction if i == 0 else self.direction

                if i == 0:
                    PushMatrix()
                    if direction == (self.cell_width, 0):  # Right
                        Rotate(origin=(x + self.cell_width / 2, y + self.cell_height / 2), angle=90)
                    elif direction == (-self.cell_width, 0):  # Left
                        Rotate(origin=(x + self.cell_width / 2, y + self.cell_height / 2), angle=270)
                    elif direction == (0, self.cell_height):  # Up
                        Rotate(origin=(x + self.cell_width / 2, y + self.cell_height / 2), angle=180)
                    elif direction == (0, -self.cell_height):  # Down
                        Rotate(origin=(x + self.cell_width / 2, y + self.cell_height / 2), angle=0)
                    Ellipse(texture=texture, pos=segment, size=(self.cell_width, self.cell_height), keep_ratio=True, allow_stretch=True)
                    PopMatrix()
                else:
                    Ellipse(texture=texture, pos=segment, size=(self.cell_width, self.cell_height), keep_ratio=False, allow_stretch=False)

            texture = Image("apple1.png").texture
            texture.wrap = "clamp_to_edge"
            Ellipse(texture=texture, pos=self.food, size=(self.cell_width, self.cell_height), keep_ratio=True, allow_stretch=True)

    def update_score(self, points):
        self.score += points
        self.score_label.text = f"Score: {self.score}"

    def reset_score(self):
        self.score = 0
        self.score_label.text = "Score: 0"
        self.high_score_label.text = f"High Score: {self.high_score}"

    def random_position(self):
        while True:
            x = randint(0, GRID_COLS - 1) * self.cell_width
            y = randint(0, GRID_ROWS - 1) * self.cell_height
            if (x, y) not in self.snake:
                return (x, y)

    def reset_game(self):
        self.alpha = .5
        with self.canvas.before:
            self.canvas.before.clear()
            Color(.5, 0, 0, 0.5)
            Rectangle(pos=self.pos, size=self.size)
        self.snake = self.initialize_snake()
        self.direction = (self.cell_width, 0)
        self.next_direction = self.direction
        self.food = self.random_position()
        self.reset_score()

    def on_key_down(self, window, key, *args):
        if (key == 273 or key == 119) and self.direction != (0, -self.cell_height):  # Вверх
            self.next_direction = (0, self.cell_height)
        elif (key == 274 or key == 115) and self.direction != (0, self.cell_height):  # Вниз
            self.next_direction = (0, -self.cell_height)
        elif (key == 275 or key == 100) and self.direction != (-self.cell_width, 0):  # Вправо
            self.next_direction = (self.cell_width, 0)
        elif (key == 276 or key == 97) and self.direction != (self.cell_width, 0):  # Влево
            self.next_direction = (-self.cell_width, 0)

class SnakeGameApp(App):

    def build(self):
        root = BoxLayout(orientation='vertical')
        top_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))

        high_score_label = Label(text="High Score: 0", size_hint=(0.5, 1), halign='left', valign='middle')
        high_score_label.bind(size=high_score_label.setter('text_size'))

        score_label = Label(text="Score: 0", size_hint=(0.5, 1), halign='right', valign='middle')
        score_label.bind(size=score_label.setter('text_size'))

        top_box.add_widget(high_score_label)
        top_box.add_widget(score_label)

        game_field = GameField(score_label, high_score_label, size_hint=(1, 0.9))

        texture = Image("Snake.png").texture
        with top_box.canvas.before:
            self.rect = Rectangle(texture=texture, size=top_box.size, pos=top_box.pos)
            top_box.bind(size=self._update_rect, pos=self._update_rect)

        root.add_widget(top_box)
        root.add_widget(game_field)

        Window.bind(on_key_down=game_field.on_key_down)

        return root

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

if __name__ == '__main__':
    SnakeGameApp().run()
