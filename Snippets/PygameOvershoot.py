#!/usr/bin/env python3

import sys, pygame

class RectInt(pygame.Rect):
    def __init__(self, x, y, w, h, speed):
        pygame.Rect.__init__(self, x, y, w, h)
        self.speed = speed

    # Overshooting is possible if `target.width - self.w` isn't divisible by
    # `self.speed`.
    def move_naive1(self, target):
        if self.right < target.get_rect().w:
            self.x += self.speed

    # Undershooting is possible if `target.width - self.w` isn't divisible by
    # `self.speed`.
    def move_naive2(self, target):
        if self.right + self.speed <= target.get_rect().w:
            self.x += self.speed

    # Move like `move_naive2()` and then cover the remaining distance to
    # correct the undershoot.
    def move_check(self, target):
        if self.right + self.speed <= target.get_rect().w:
            self.x += self.speed
        elif self.right != target.get_rect().w:
            self.right = target.get_rect().w

    # Overshoot then correct by clamping.
    def move_clamp(self, target):
        self.x += self.speed
        self.clamp_ip(target.get_rect())

# RectFloat handle floating point coordinates without flooring them.
class RectFloat:
    def __init__(self, x, y, w, h, speed):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = speed

    def move_clamp(self, target):
        self.x += self.speed
        if self.x + self.w > target.get_rect().w:
            self.x = target.get_rect().w - self.w

    def toPygRect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

class Scene:
    def __init__(self):
        self.r10 = RectInt(  10,   0, 10, 15, speed = 1)
        self.r11 = RectInt(  10,  20, 10, 15, speed = 6)
        self.r12 = RectInt(  10,  40, 10, 15, speed = 6)
        self.r13 = RectInt(  10,  60, 10, 15, speed = 6)
        self.r14 = RectInt(  10,  80, 10, 15, speed = 6)
        self.r20 = RectFloat(10, 100, 10, 15, speed = 1.5)

    def update(self, target):
        self.r10.move_naive1(target) # no overshoot because r1a.speed = 1
        self.r11.move_naive1(target) # overshoot
        self.r12.move_naive2(target) # undershoot
        self.r13.move_check(target) # ok
        self.r14.move_clamp(target) # ok
        self.r20.move_clamp(target) # ok
        print(f'{self.r10.x=} {self.r11.x=} {self.r12.x=} {self.r13.x=} {self.r14.x=} {self.r20.x=}')

    def draw(self, target):
        target.fill((0, 0, 0))
        pygame.draw.rect(target, (  0,   0, 255), self.r10)
        pygame.draw.rect(target, (  0, 255,   0), self.r11)
        pygame.draw.rect(target, (  0, 255, 255), self.r12)
        pygame.draw.rect(target, (255,   0,   0), self.r13)
        pygame.draw.rect(target, (255,   0, 255), self.r14)
        pygame.draw.rect(target, (255, 255,   0), self.r20.toPygRect())

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((160, 200))
    clock = pygame.time.Clock()
    scene = Scene()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        scene.update(screen)
        scene.draw(screen)

        clock.tick(60)
        pygame.display.flip()
