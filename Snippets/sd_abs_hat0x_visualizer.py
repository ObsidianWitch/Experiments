#!/usr/bin/env python3

import pygame, libevdev
from libevdev import EV_ABS

dev = libevdev.Device(open('/dev/input/by-id/usb-Valve_Software_Steam_Controller_123456789ABCDEF-if02-event-joystick', 'rb'))
hat0x_info = dev.absinfo[EV_ABS.ABS_HAT0X]
offset = hat0x_info.maximum // 100
width = (hat0x_info.maximum * 2 + 1) // 100

pygame.init()
screen = pygame.display.set_mode((width, width))
clock = pygame.time.Clock()

x, y = (0, 0)
while ev_in := next(dev.events()):
    pygame.event.pump()

    if (ev_in.code == EV_ABS.ABS_HAT0X):
        x = (ev_in.value // 100) + offset
    elif (ev_in.code == EV_ABS.ABS_HAT0Y):
        y = -(ev_in.value // 100) + offset
    print(x,y)


    screen.fill((0, 0, 0))
    for i in range(width // 4, width, width // 4):
        pygame.draw.line(screen, (0, 255, 0), (i, 0), (i, width), width=11)
        pygame.draw.line(screen, (0, 255, 0), (0, i), (width, i), width=11)
    pygame.draw.circle(screen, (255, 0, 0), (x, y), 10)
    pygame.display.flip()
