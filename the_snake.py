import random
from itertools import product
from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE_DIRECTIONS = {UP: DOWN, LEFT: RIGHT, RIGHT: LEFT, DOWN: UP}

KEYS_AND_DIRECTIONS = {pygame.K_UP: UP, pygame.K_DOWN: DOWN,
                       pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT,
                       pygame.K_w: UP, pygame.K_s: DOWN,
                       pygame.K_a: LEFT, pygame.K_d: RIGHT}

BOARD_BACKGROUND_COLOR = (187, 187, 187)

# Цвет границы ячейки
BORDER_COLOR = (0, 0, 0)

BORDER_SIZE = 1

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

DEFAULT_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Скорость движения змейки:
SPEED = 20

DEFAULT_COLOR = (0, 0, 0)

ALL_CELLS = set(product(range(0, SCREEN_WIDTH, GRID_SIZE),
                        range(0, SCREEN_HEIGHT, GRID_SIZE)))

# Настройка игрового окна:
screen = (pygame.display
          .set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32))

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка. Для выхода нажмите Esc')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Base class for game objects"""

    def __init__(self, position: tuple[int, int] = DEFAULT_POSITION,
                 body_color: tuple[int, int, int] = DEFAULT_COLOR):

        self.position: tuple[int, int] = position
        self.body_color: tuple[int, int, int] = body_color

    def draw(self):
        """Draws basic rectangle"""
        raise NotImplementedError('This method must be '
                                  'overridden by a subclass.')

    def draw_rectangle(self, position: tuple[int, int],
                       color: tuple[int, int, int] = None,
                       border_color: tuple[int, int, int] = None):
        """Draws rectangle"""
        rect_color = color or self.body_color
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, rect_color, rect)
        if border_color is not None:
            pygame.draw.rect(screen, border_color, rect, BORDER_SIZE)


class Apple(GameObject):
    """Class for apple object"""

    def __init__(self, restricted_positions=None,
                 body_color: tuple[int, int, int] = APPLE_COLOR):

        super().__init__(body_color=body_color)
        restricted_positions = restricted_positions or []
        self.randomize_position(restricted_positions)

    def randomize_position(self, restricted_positions: list[tuple[int, int]]):
        """Sets apple position randomly avoiding restricted areas"""
        self.position = (random.choice(tuple(ALL_CELLS
                                             - set(restricted_positions))))

    def draw(self):
        """Draws apple"""
        self.draw_rectangle(self.position)


class Snake(GameObject):
    """Class for snake object"""

    def __init__(self, body_color: tuple[int, int, int] = SNAKE_COLOR):

        super().__init__(body_color=body_color)
        self.reset()

    def move(self):
        """Moves snake in direction"""
        x_head, y_head = self.get_head_position()
        direction_x, direction_y = self.direction
        self.positions.insert(0, (
            (x_head + GRID_SIZE * direction_x) % SCREEN_WIDTH,
            (y_head + GRID_SIZE * direction_y) % SCREEN_HEIGHT
        ))
        if self.length < len(self.positions):
            self.last = self.positions.pop()
        else:
            self.last = None

    def get_head_position(self) -> tuple[int, int]:
        """Gets snake head position"""
        return self.positions[0]

    def update_direction(self, direction: tuple[int, int]):
        """Updates snake direction"""
        if OPPOSITE_DIRECTIONS[direction] != self.direction:
            self.direction = direction

    def eat_apple(self):
        """Sets snake's length if it consumes apple"""
        self.length = self.length + 1

    def get_body(self) -> list[tuple[int, int]]:
        """Returns snake body"""
        return self.positions[1:]

    def draw(self):
        """Draws snake's head"""
        self.draw_rectangle(self.get_head_position(),
                            border_color=BORDER_COLOR)
        if self.last:
            self.draw_rectangle(self.last, BOARD_BACKGROUND_COLOR)

    def reset(self):
        """Resets snake position and direction"""
        self.positions = [DEFAULT_POSITION]
        self.direction = choice([UP, DOWN, RIGHT, LEFT])
        self.length = 1
        self.last = None


def set_game(apple: Apple, snake: Snake):
    """Sets up game at default start"""
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.reset()
    apple.randomize_position(snake.positions)
    snake.draw()
    apple.draw()


def handle_keys(snake: Snake):
    """Handles keyboard events"""
    for event in pygame.event.get():
        if (event.type == pygame.QUIT
                or (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            direction = KEYS_AND_DIRECTIONS.get(event.key)
            if direction:
                snake.update_direction(direction)


def main():
    """Main function"""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    set_game(apple, snake)
    while True:
        handle_keys(snake)
        snake.move()
        if snake.get_head_position() in snake.get_body():
            set_game(apple, snake)
            continue
        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)
            snake.eat_apple()
            apple.draw()
        snake.draw()
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
