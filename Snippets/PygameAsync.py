#!/usr/bin/env python3

import sys, time, asyncio
import pygame # https://pypi.org/project/pygame/

class Window:
    def __init__(self, size, ups, rps):
        pygame.init()
        self.surface = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.ups = ups
        self.rps = rps

    async def update(self, fun):
        while True:
            time_start = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.event_loop.stop()

            fun(self.surface)

            time_end = time.time()
            delta = time_end - time_start
            await asyncio.sleep((1 / self.ups) - delta)
            print(f"UPS: {1 / (time.time() - time_start)}")

    async def render(self, fun):
        while True:
            time_start = time.time()

            fun(self.surface)
            pygame.display.flip()

            time_end = time.time()
            delta = time_end - time_start
            await asyncio.sleep(max(0, (1 / self.rps) - delta))
            print(f"RPS: {1 / (time.time() - time_start)}")

    def loop(self, update, render):
        self.event_loop = asyncio.get_event_loop()
        self.event_loop.create_task(self.update(update))
        self.event_loop.create_task(self.render(render))
        self.event_loop.run_forever()

class Game:
    def __init__(self):
        self.rect = pygame.Rect(10, 10, 10, 10)
        self.speed = 2

    def update(self, target):
        target_rect = target.get_rect()
        self.rect.x += self.speed
        self.rect.clamp_ip(target_rect)
        if (self.rect.right == target_rect.right) \
            or (self.rect.left == target_rect.left) \
        : self.speed *= -1

    def render(self, target):
        target.fill((0, 0, 0))
        pygame.draw.rect(target, (255, 255, 255), self.rect)

if __name__ == "__main__":
    window = Window(size=(160,200), ups=60, rps=30)
    game = Game()
    window.loop(game.update, game.render)
