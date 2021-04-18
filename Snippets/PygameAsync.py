#!/usr/bin/env python3

import sys, asyncio, argparse
import pygame # https://pypi.org/project/pygame/

class Window:
    def __init__(self, size, ups, rps):
        pygame.init()
        self.surface = pygame.display.set_mode(size)
        self.ups = ups
        self.rps = rps

    async def asyncupdate(self, fun):
        uclock = pygame.time.Clock()
        while True:
            time_start = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.event_loop.stop()

            fun(self.surface)

            time_end = pygame.time.get_ticks()
            delta = (time_end - time_start) / 1000
            await asyncio.sleep(max(0, (1 / self.ups) - delta))
            uclock.tick()
            print(f"UPS: {uclock.get_fps()}")

    async def asyncrender(self, fun):
        rclock = pygame.time.Clock()
        while True:
            time_start = pygame.time.get_ticks()

            fun(self.surface)
            pygame.display.flip()

            time_end = pygame.time.get_ticks()
            delta = (time_end - time_start) / 1000
            await asyncio.sleep(max(0, (1 / self.rps) - delta))
            rclock.tick()
            print(f"RPS: {rclock.get_fps()}")

    def asyncloop(self, update, render):
        self.event_loop = asyncio.get_event_loop()
        self.event_loop.create_task(self.asyncupdate(update))
        self.event_loop.create_task(self.asyncrender(render))
        self.event_loop.run_forever()

    def syncloop(self, update, render):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            update(self.surface)
            render(self.surface)
            pygame.display.flip()

            clock.tick(self.ups)
            print(f"FPS: {clock.get_fps()}")

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
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('sync', 'async'))
    parser.add_argument('ups', type=int)
    parser.add_argument('rps', type=int) # unused in sync mode
    args = parser.parse_args()

    window = Window(size=(160,200), ups=args.ups, rps=args.rps)
    game = Game()
    if args.mode == 'sync':
        window.syncloop(game.update, game.render)
    elif args.mode == 'async':
        window.asyncloop(game.update, game.render)
