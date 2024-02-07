import pygame
from collections import namedtuple
from directions import Direction
from settings import Settings
import random
import numpy

pygame.init()

font = pygame.font.SysFont("arial", 25)

Point = namedtuple("Point", "x,y")


class SnakeGameAI:

    def __init__(self, w=640, h=480) -> None:
        self.w = w
        self.h = h

        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT
        self.stt = Settings()

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [
            self.head,
            Point(self.head.x - self.stt.block_size, self.head.y),
            Point(self.head.x - (2 * self.stt.block_size), self.head.y),
        ]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        b_s = self.stt.block_size
        x = random.randint(0, (self.w - b_s) // b_s) * b_s
        y = random.randint(0, (self.h - b_s) // b_s) * b_s
        self.food = Point(x, y)

        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

        self.move(action)
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(self.stt.speed)

        return reward, game_over, self.score

    def is_collision(self, point=None):
        if point == None:
            point = self.head

        if (
            point.x > self.w - self.stt.block_size
            or point.x < 0
            or point.y > self.h - self.stt.block_size
            or point.y < 0
        ):
            return True
        if point in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        b_s = self.stt.block_size
        self.display.fill(self.stt.black)

        for pt in self.snake:
            pygame.draw.rect(
                self.display, self.stt.blue_one, pygame.Rect(pt.x, pt.y, b_s, b_s)
            )
            pygame.draw.rect(
                self.display, self.stt.blue_two, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12)
            )

        pygame.draw.rect(
            self.display, self.stt.red, pygame.Rect(self.food.x, self.food.y, b_s, b_s)
        )

        text = font.render("Score: " + str(self.score), True, self.stt.white)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        curr_index = clock_wise.index(self.direction)

        if numpy.array_equal(action, [1, 0, 0]):
            new_direct = clock_wise[curr_index]  # no change
        elif numpy.array_equal(action, [0, 1, 0]):
            next_index = (curr_index + 1) % 4
            new_direct = clock_wise[next_index]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_index = (curr_index - 1) % 4
            new_direct = clock_wise[next_index]  # left turn r -> u -> l -> d

        self.direction = new_direct

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += self.stt.block_size
        elif self.direction == Direction.LEFT:
            x -= self.stt.block_size
        elif self.direction == Direction.UP:
            y -= self.stt.block_size
        elif self.direction == Direction.DOWN:
            y += self.stt.block_size

        self.head = Point(x, y)

    def quit(self):
        pygame.quit()
        quit()
