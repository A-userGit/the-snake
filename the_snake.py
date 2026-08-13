import random
import pygame

from collections import deque
from abc import ABC
from itertools import islice
from pygame import Surface

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

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = (pygame.display
          .set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32))

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()

class GameEngine:
    """Processes game logic"""
    def __init__(self, screen: Surface, field_width: int = 0,
                 field_height: int = 0, grid_size: int = 0,
                 field_color: tuple[int, int, int] =(0, 0, 0)) -> None:
        self.__width = field_width
        self.__height = field_height
        self.__grid_size = grid_size
        self.__screen = screen
        self.__color = field_color

    def set_game(self, snake: Snake, apple: Apple,
                 position: tuple[int, int] = (0, 0),
                direction: tuple[int, int] = (0, 0)):
        """Sets up game at default start"""
        self.__screen.fill(self.__color)
        apple.randomize_position([position], self.__width,
                                 self.__height, self.__grid_size)
        apple.draw(self.__screen, self.__grid_size)
        snake.reset(position, direction)
        snake.draw(self.__screen, self.__grid_size)

    def check_collisions(self, first_body: tuple[int, int] = (0, 0),
                         second_body: tuple[int, int] = (0, 0))-> bool:
        """Checks collisions between two objects"""
        if first_body == second_body:
            return True
        return False

    def check_collisions_with_area(self,
                                   area_coordinates: list[tuple[int, int]],
                                   second_object: tuple[int, int] =
                                   (0, 0))-> bool:
        """Checks collisions between object and set of objects"""
        for coordinates_set in area_coordinates:
            if self.check_collisions(coordinates_set, second_object):
                return True
        return False

    def redraw_field_part(self, coordinates: tuple[int, int]):
        """Redraws field part with basic color"""
        last_rect = pygame.Rect(coordinates, (self.__grid_size,
                                              self.__grid_size))
        pygame.draw.rect(screen, self.__color, last_rect)

    def process_movement(self, snake: Snake, apple: Apple)-> bool:
        """Processes movement of snake and its collisions with apple and itself"""
        tail_position = snake.get_tail_position()
        tail_moved = snake.move(self.__grid_size, self.__width, self.__height)
        collided = self.check_collisions_with_area(snake.body,
                                                   snake.get_head_position())
        if collided:
            return False
        if tail_moved:
            self.redraw_field_part(tail_position)
        apple_eaten = self.check_collisions(snake.get_head_position(),
                                            apple.position)
        if apple_eaten:
            snake.eat_apple()
            restricted_positions = snake.positions
            restricted_positions.append(tail_position)
            apple.randomize_position(list(restricted_positions),
                                     self.__width, self.__height,
                                     self.__grid_size)
            apple.draw(self.__screen, self.__grid_size)
        snake.draw(self.__screen, self.__grid_size)
        return True

class GameObject(ABC):
    """Base class for game objects"""
    def __init__(self, position: tuple[int, int] = (0, 0),
                 body_color: tuple[int, int, int] = (0, 0, 0)):

        self._position: tuple[int, int] = position
        self._body_color: tuple[int, int, int] = body_color

    @property
    def position(self)-> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, new_position: tuple[int, int]):
        self._position = new_position

    @property
    def body_color(self)-> tuple[int, int, int]:
        return self._body_color

    #method is abstract but i cant use @abstract method because autotests will crash
    def draw(self, field: Surface, grid_size: int):
        pass



class Apple(GameObject):
    """Class for apple object"""
    def __init__(self, position: tuple[int, int] = (0, 0),
                 body_color: tuple[int, int, int] = (0, 0, 0),
                 border_size: int = 0,
                 border_color: tuple[int, int, int]=(0, 0, 0)):

        super().__init__(position, body_color)
        self.__border_color = border_color
        self.__border_size = border_size

    def randomize_position(self, restricted_positions: list[tuple[int, int]],
                           field_width: int = 0, field_height: int = 0,
                           grid_step: int = 0):
        """Sets apple position randomly avoiding restricted areas"""
        position_found = False
        x_pos = 0
        y_pos = 0
        while not position_found:
            x_pos = random.randrange(0, field_width, grid_step)
            y_pos = random.randrange(0, field_height, grid_step)
            position_found = True
            for position in restricted_positions:
                restricted_x, restricted_y = position
                if restricted_x == x_pos and restricted_y == y_pos:
                    position_found = False
                    break
        self.position = (x_pos, y_pos)


    def draw(self, field: Surface, grid_size: int):
        """Draws apple"""
        rect = pygame.Rect(self._position, (grid_size, grid_size))
        pygame.draw.rect(field, self._body_color, rect)
        pygame.draw.rect(field, self.__border_color, rect, self.__border_size)

class Snake(GameObject):
    """Class for snake object"""
    def __init__(self, position: tuple[int, int] = (0, 0),
                 body_color: tuple[int, int, int] = (0, 0, 0),
                 direction: tuple[int, int] = (1,0),
                 border_color: tuple[int, int, int] = (0,0,0),
                 border_size: int = 0):

        super().__init__(position, body_color)
        self.__positions = deque([position])
        self.__direction = direction
        self.__border_color = border_color
        self.__border_size = border_size
        self.__length = 1

    @property
    def direction(self)->tuple[int, int]:
        return self.__direction

    @direction.setter
    def direction(self, value: tuple[int, int]):
        self.__direction = value

    @property
    def positions(self)-> deque[tuple[int, int]]:
        return self.__positions

    @property
    def body(self)-> list[tuple[int, int]]:
        return list(islice(self.__positions, 1, None))

    def move(self, step: int, board_width: int = 0, board_height: int = 0):
        """Moves snake in direction"""
        x_head, y_head = self.__positions[0]
        direction_x, direction_y = self.__direction
        x_new_head = x_head + step * direction_x
        y_new_head = y_head + step * direction_y
        if x_new_head >= board_width:
            x_new_head = 0
        if x_new_head < 0:
            x_new_head = board_width - step
        if y_new_head >= board_height:
            y_new_head = 0
        if y_new_head < 0:
            y_new_head = board_height - step
        self.__positions.appendleft((x_new_head, y_new_head))
        if self.__length < len(self.__positions):
            self.__positions.pop()
            return True
        return False

    def reset(self, position: tuple[int, int] = (0, 0),
              direction: tuple[int, int] = (0, 0)):
        """Resets snake position and direction"""
        self._position = position
        self.__direction: tuple[int, int] = direction
        self.__positions: deque[tuple[int, int]] = (
            deque([position]))

    def draw(self, field: Surface, grid_size: int):
        """Draws snake's head"""
        head_rect = pygame.Rect(self.__positions[0], (grid_size, grid_size))
        pygame.draw.rect(field, self._body_color, head_rect)
        pygame.draw.rect(field, self.__border_color, head_rect,
                         self.__border_size)

    def get_head_position(self)-> tuple[int, int]:
        return self.__positions[0]

    def update_direction(self, direction: tuple[int, int] = (0, 0)):
        self.__direction = direction

    def eat_apple(self):
        self.__length =+ 1

    def get_tail_position(self)-> tuple[int, int]:
        return self.__positions[-1]


def handle_keys(game_object: Snake):
    """Handles keyboard events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.direction = RIGHT


def main():
    start_position = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    start_direction = (1, 0)
    # Инициализация PyGame:
    pygame.init()
    engine = GameEngine(screen, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE,
                        BOARD_BACKGROUND_COLOR)
    snake = Snake(start_position, SNAKE_COLOR, start_direction,
                  BORDER_COLOR, 1)
    apple = Apple((0, 0), APPLE_COLOR, 1, BORDER_COLOR)
    engine.set_game(snake, apple, start_position, start_direction)
    while True:
        handle_keys(snake)
        moved = engine.process_movement(snake, apple)
        if not moved:
            engine.set_game(snake, apple, start_position, start_direction)
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
