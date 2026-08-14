from itertools import product
import random

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
                       pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT}

BOARD_BACKGROUND_COLOR = (187, 187, 187)

# Цвет границы ячейки
BORDER_COLOR = (187, 187, 187)

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
        self.draw_rectangle(self.position)


    def draw_rectangle(self, position: tuple[int, int],
                       color: tuple[int, int, int] = DEFAULT_COLOR):
        """Draws rectangle"""
        if color == DEFAULT_COLOR:
            color = self.body_color
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, BORDER_SIZE)


class Apple(GameObject):
    """Class for apple object"""

    def __init__(self, restricted_positions=None,
                 body_color: tuple[int, int, int] = APPLE_COLOR):

        super().__init__(body_color = body_color)
        if restricted_positions is None:
            restricted_positions = list([])
        self.randomize_position(restricted_positions)

    def randomize_position(self, restricted_positions: list[tuple[int, int]]):
        """Sets apple position randomly avoiding restricted areas"""
        pos = (random.choice(tuple(ALL_CELLS -
                                             set(restricted_positions))))
        self.position = pos


class Snake(GameObject):
    """Class for snake object"""

    def __init__(self, body_color: tuple[int, int, int] = SNAKE_COLOR,
                 direction: tuple[int, int] = DEFAULT_DIRECTION):

        super().__init__(body_color = body_color)
        self.positions = [DEFAULT_POSITION]
        self.direction = direction
        self.length = 1

    def move(self):
        """Moves snake in direction"""
        x_head, y_head = self.get_head_position()
        direction_x, direction_y = self.direction
        x_new_head = (x_head + GRID_SIZE * direction_x) % SCREEN_WIDTH
        y_new_head = (y_head + GRID_SIZE * direction_y) % SCREEN_HEIGHT
        self.positions.insert(0, (x_new_head, y_new_head))
        if self.length < len(self.positions):
            self.positions.pop()
            return True
        return False

    def get_head_position(self) -> tuple[int, int]:
        """Gets snake head position"""
        return self.positions[0]

    def update_direction(self, direction: tuple[int, int] = (0, 0)):
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
        return self.positions[1:]

    def draw(self):
        """Draws snake's head"""
        self.draw_rectangle(self.get_head_position())

    def reset(self):
        """Resets snake position and direction"""
        self.positions = [DEFAULT_POSITION]
        self.direction = DEFAULT_DIRECTION
        self.length = 1


class GameEngine:
    """Processes game logic"""

    def __init__(self, snake: Snake):
        self.snake = snake
        self.apple = None

    def set_game(self):
        """Sets up game at default start"""
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.snake.reset()
        self.apple = Apple(self.snake.positions)
        self.snake.draw()
        self.apple.draw()


    def check_collisions(self, first_body: tuple[int, int] = (0, 0),
                         second_body: tuple[int, int] = (0, 0)) -> bool:
        """Checks collisions between two objects"""
        return first_body == second_body

    def check_collisions_with_area(self,
                                   area_coordinates: list[tuple[int, int]],
                                   second_object: tuple[int, int] =
                                   DEFAULT_POSITION) -> bool:
        """Checks collisions between object and set of objects"""
        return second_object in area_coordinates

    def process_movement(self) -> bool:
        """Processes movement of snake and its collisions with apple, itself"""
        tail_position = self.snake.get_tail_position()
        tail_moved = self.snake.move()
        collided = self.check_collisions_with_area(
            self.snake.get_body(), self.snake.get_head_position())
        if collided:
            return False
        if tail_moved:
            self.snake.draw_rectangle(tail_position, BOARD_BACKGROUND_COLOR)
        apple_eaten = self.check_collisions(self.snake.get_head_position(),
                                            self.apple.position)
        if apple_eaten:
            self.snake.eat_apple()
            restricted_positions = self.snake.positions
            restricted_positions.append(tail_position)
            self.apple = Apple(restricted_positions)
            self.apple.draw()
        self.snake.draw()
        return True

def exit_game():
        """Exits game"""
        pygame.quit()
        raise SystemExit

def handle_keys(snake: Snake):
    """Handles keyboard events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
               exit_game()
            direction = KEYS_AND_DIRECTIONS.get(event.key)
            if direction:
                snake.update_direction(direction)


def main():
    """Main function"""

    pygame.init()
    snake = Snake()
    engine = GameEngine(snake)
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
