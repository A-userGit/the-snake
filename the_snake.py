import random
from random import choice
from itertools import product

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

DEFAULT_DIRECTION = (1, 0)

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
        raise NotImplementedError('This method must be overridden by a subclass.')

    def draw_rectangle(self, position: tuple[int, int],
                       color: tuple[int, int, int] = None,
                       border_color: tuple[int, int, int] = None):
        """Draws rectangle"""
        rect_color = color or self.body_color
        rect_border_color = border_color or BORDER_COLOR
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, rect_color, rect)
        pygame.draw.rect(screen, rect_border_color, rect, BORDER_SIZE)


class Apple(GameObject):
    """Class for apple object"""

    def __init__(self, restricted_positions=None,
                 body_color: tuple[int, int, int] = APPLE_COLOR):

        super().__init__(body_color=body_color)
        restricted_positions = restricted_positions or []
        self.randomize_position(restricted_positions)

    def randomize_position(self, restricted_positions: list[tuple[int, int]]):
        """Sets apple position randomly avoiding restricted areas"""
        self.position = (random.choice(tuple(ALL_CELLS -
                                             set(restricted_positions))))

    def draw(self):
        """Draws apple"""
        self.draw_rectangle(self.position, APPLE_COLOR)


class Snake(GameObject):
    """Class for snake object"""

    def __init__(self, body_color: tuple[int, int, int] = SNAKE_COLOR):

        super().__init__(body_color=body_color)
        self.reset()

    def move(self):
        """Moves snake in direction"""
        x_head, y_head = self.get_head_position()
        direction_x, direction_y = self.direction
        self.positions.insert(0,
                              ((x_head + GRID_SIZE * direction_x) %
                               SCREEN_WIDTH,
                                  (y_head + GRID_SIZE * direction_y) %
                               SCREEN_HEIGHT))
        if self.length < len(self.positions):
            self.positions.pop()
            return True
        return False

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

    def get_tail_position(self) -> tuple[int, int]:
        """Gets snake tail position"""
        return self.positions[-1]

    def get_body(self) -> list[tuple[int, int]]:
        """Returns snake body"""
        return self.positions[1:]

    def draw(self):
        """Draws snake's head"""
        self.draw_rectangle(self.get_head_position())

    def reset(self):
        """Resets snake position and direction"""
        self.positions = [DEFAULT_POSITION]
        x_direction = random.randint(-1, 1)
        y_direction = 0
        if x_direction == 0:
            y_direction = choice([-1, 1])
        self.direction = (x_direction, y_direction)
        self.length = 1


class GameEngine:
    """Processes game logic"""

    def __init__(self, snake: Snake, apple: Apple):
        self.snake = snake
        self.apple = apple

    def set_game(self):
        """Sets up game at default start"""
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.snake.reset()
        self.apple.randomize_position(self.snake.positions)
        self.snake.draw()
        self.apple.draw()

    def process_movement(self) -> bool:
        """Processes movement of snake and its collisions with apple, itself"""
        tail_position = self.snake.get_tail_position()
        tail_moved = self.snake.move()
        collided = self.snake.get_head_position() in self.snake.get_body()
        if collided:
            return False
        if tail_moved:
            self.snake.draw_rectangle(tail_position, BOARD_BACKGROUND_COLOR,
                                      BOARD_BACKGROUND_COLOR)
        apple_eaten = (self.snake.get_head_position() == self.apple.position)
        if apple_eaten:
            self.snake.eat_apple()
            restricted_positions = self.snake.positions
            restricted_positions.append(tail_position)
            self.apple = Apple(restricted_positions)
            self.apple.draw()
        self.snake.draw()
        return True


def handle_keys(snake: Snake):
    """Handles keyboard events"""
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
                (event.type == pygame.KEYDOWN and
                 event.key == pygame.K_ESCAPE)):
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
    engine = GameEngine(snake, apple)
    engine.set_game()
    while True:
        handle_keys(engine.snake)
        moved = engine.process_movement()
        if not moved:
            engine.set_game()
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
