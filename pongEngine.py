from random import uniform, choice
from typing import Union, Tuple, List


class Ball:
    def __init__(self, game, radius, speed):
        self._game = game
        self._speed = speed
        self._radius = radius
        self.__dx = 0
        self.__dy = 0
        self.__x = game.width / 2 - self._radius
        self.__y = game.height / 2 - self._radius

    @property
    def position(self):
        return self.__x, self.__y

    @property
    def dx(self):
        return self.__dx

    @property
    def dy(self):
        return self.__dy

    @property
    def radius(self):
        return self._radius

    def starting_position(self):
        self.__dx = 0
        self.__dy = 0
        self.__x = self._game.width / 2 - self._radius
        self.__y = self._game.height / 2 - self._radius

    def shoot(self):
        self.__dx = choice([-1, 1]) * uniform(self._speed * 0.2, self._speed * 0.8)
        self.__dy = choice([-1, 1]) * (self._speed - abs(self.__dx))

    def update(self):
        self.__x += self.__dx
        self.__y += self.__dy

        if self.__y < self._radius * 2 or self.__y > self._game.height - self._radius * 2:
            self.__dy = -self.__dy

        self._game.score = [self.__x < self._radius, self.__x > self._game.width - self._radius]

        if self.__x < self._radius or self.__x > self._game.width - self._radius:
            self._game.starting_position()

        if self._game.left_paddle.intersect(self) or self._game.right_paddle.intersect(self):
            self.__dx = -self.__dx


class Padle:
    def __init__(self, game, speed, left=True):
        self._game = game
        self._speed = speed
        self._left = left
        self.__x = game.width * 0.05 if left else game.width * 0.95
        self._height = game.height * 0.15
        self.__y = game.height / 2 - self._height / 2
        self._width = self._height / 10

    def moveUp(self):
        self.__y -= self._speed
        if self.__y < 0:
            self.__y = 0

    def moveDown(self):
        self.__y += self._speed
        if self.__y + self.height > self._game.height:
            self.__y = self._game.height - self.height

    def starting_position(self):
        self.__x = self._game.width * 0.05 if self._left else self._game.width * 0.95
        self.__y = self._game.height / 2 - self._height / 2

    @property
    def position(self):
        return self.__x, self.__y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def intersect(self, ball):
        ball_x, ball_y = ball.position
        radius = ball.radius

        return ((ball_x - radius < self.__x + self.width and self._left) or \
                (ball_x + radius > self.__x and not self._left)) and \
            ball_y < self.__y + self.height and \
            ball_y > self.__y


class PongGameEngine:
    def __init__(self,
                 size: Union[Tuple[int, int], List[int]],
                 ball_radius=2, ball_speed=5,
                 paddle_speed=5):
        self.__width, self.__height = size

        self.ball = Ball(self, ball_radius, ball_speed)
        self.left_paddle = Padle(self, paddle_speed)
        self.right_paddle = Padle(self, paddle_speed, left=False)

        self.__score = [0, 0]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, score):
        self.__score = [self.__score[0] + score[0], self.__score[1] + score[1]]

    def starting_position(self):
        self.ball.starting_position()
        self.left_paddle.starting_position()
        self.right_paddle.starting_position()

    def restart(self):
        self.__score = [0, 0]
        self.starting_position()

    def update(self):
        self.ball.update()
