#!/usr/bin/env python3

import sys
from collections import defaultdict
from enum import Enum
from libevdev import *
from libevdev import EV_KEY as K

LAYOUT = [[[K.KEY_1, K.KEY_2, K.KEY_3, K.KEY_4],
           [K.KEY_5, K.KEY_6, K.KEY_7, K.KEY_8],
           [K.KEY_9, K.KEY_0, K.KEY_MINUS, K.KEY_EQUAL]],
          [[K.KEY_Q, K.KEY_W, K.KEY_E, K.KEY_R],
           [K.KEY_T, K.KEY_Y, K.KEY_U, K.KEY_I],
           [K.KEY_O, K.KEY_P, K.KEY_LEFTBRACE, K.KEY_RIGHTBRACE]],
          [[K.KEY_A, K.KEY_S, K.KEY_D, K.KEY_F],
           [K.KEY_G, K.KEY_H, K.KEY_J, K.KEY_K],
           [K.KEY_L, K.KEY_SEMICOLON, K.KEY_APOSTROPHE, K.KEY_BACKSLASH]],
          [[K.KEY_Z, K.KEY_X, K.KEY_C, K.KEY_V],
           [K.KEY_B, K.KEY_N, K.KEY_M, K.KEY_COMMA],
           [K.KEY_DOT, K.KEY_SLASH, K.KEY_GRAVE, K.KEY_102ND]],
          [[K.KEY_F1, K.KEY_F2, K.KEY_F3, K.KEY_F4],
           [K.KEY_F5, K.KEY_F6, K.KEY_F7, K.KEY_F8],
           [K.KEY_F9, K.KEY_SYSRQ, K.KEY_SCROLLLOCK, K.KEY_PAUSE]]]

class SDMap:
    DEVICE = '/dev/input/by-id/usb-Valve_Software_Steam_Controller_123456789ABCDEF-if02-event-joystick'

    def __init__(self):
        # input
        fd = open(self.DEVICE, 'rb')
        self.dev_in = Device(fd)
        self.dev_in.grab()
        self.cache_in = defaultdict(lambda: 0)

        # keyboard
        self.dev_kbd = Device()
        self.dev_kbd.name = 'Steam Deck sdmapd keyboard'
        self.dev_kbd.enable(EV_KEY.KEY_PAGEUP)
        self.dev_kbd.enable(EV_KEY.KEY_PAGEDOWN)
        self.dev_kbd.enable(EV_KEY.KEY_HOME)
        self.dev_kbd.enable(EV_KEY.KEY_END)
        self.dev_kbd.enable(EV_KEY.KEY_UP)
        self.dev_kbd.enable(EV_KEY.KEY_DOWN)
        self.dev_kbd.enable(EV_KEY.KEY_LEFT)
        self.dev_kbd.enable(EV_KEY.KEY_RIGHT)
        self.dev_kbd.enable(EV_KEY.KEY_LEFTSHIFT)
        self.dev_kbd.enable(EV_KEY.KEY_LEFTCTRL)
        self.dev_kbd.enable(EV_KEY.KEY_LEFTMETA)
        self.dev_kbd.enable(EV_KEY.KEY_LEFTALT)
        self.dev_kbd.enable(EV_KEY.KEY_RIGHTALT)
        self.dev_kbd.enable(EV_KEY.KEY_ENTER)
        self.dev_kbd.enable(EV_KEY.KEY_ESC)
        self.dev_kbd.enable(EV_KEY.KEY_BACKSPACE)
        self.dev_kbd.enable(EV_KEY.KEY_SPACE)
        self.dev_kbd.enable(EV_KEY.KEY_TAB)
        self.dev_kbd.enable(EV_KEY.KEY_COMPOSE)
        self.dev_kbd.enable(EV_KEY.KEY_DELETE)
        for row in LAYOUT:
            for col in row:
                for key in col:
                    if key is None: continue
                    self.dev_kbd.enable(key)
        self.dev_kbd = self.dev_kbd.create_uinput_device()
        self.kbd_mode = True

        # trackapd
        self.dev_trackpad = Device()
        self.dev_trackpad.name = 'Steam Deck sdmapd trackpad'
        self.dev_trackpad.enable(EV_KEY.BTN_LEFT)
        self.dev_trackpad.enable(EV_KEY.BTN_RIGHT)
        self.dev_trackpad.enable(EV_KEY.BTN_MIDDLE)
        self.dev_trackpad.enable(EV_REL.REL_X)
        self.dev_trackpad.enable(EV_REL.REL_Y)
        self.dev_trackpad = self.dev_trackpad.create_uinput_device()
        self.touch = False

    # Map the minimum and maximum values of a joystick axis to the `key_min` and
    # `key_max` events.
    def joy2keys(self, ev_in, key_min, key_max):
        absinfo = self.dev_in.absinfo[ev_in.code]
        if abs(ev_in.value) <= absinfo.resolution:
            return [InputEvent(key_min, 0), InputEvent(key_max, 0)]
        elif ev_in.value == absinfo.minimum:
            return [InputEvent(key_min, 1)]
        elif ev_in.value == absinfo.maximum:
            return [InputEvent(key_max, 1)]
        else:
            return []

    def abs2rel(self, ev_in, rel_out, coeff):
        if (not ev_in.value) or (not self.cache_in[ev_in.code]):
            return []
        else:
            delta = ev_in.value - self.cache_in[ev_in.code]
            return [InputEvent(rel_out, int(delta * coeff))]

    # Returns the position on the virtual keyboard based on the position of
    # ABS_HAT0. Return None if ABS_HAT0 isn't used.
    def vkbd_keypos(self, evt_in):
        absinfo = self.dev_in.absinfo[EV_ABS.ABS_HAT0X]

        absx = evt_in.value() if evt_in.code == EV_ABS.ABS_HAT0X \
          else self.cache_in[EV_ABS.ABS_HAT0X]
        absy = evt_in.value() if evt_in.code == EV_ABS.ABS_HAT0Y \
          else self.cache_in[EV_ABS.ABS_HAT0Y]
        if absx == 0 and absy == 0: return None

        y = abs((absy - absinfo.maximum) * len(LAYOUT))
        y /= (absinfo.maximum * 2) + 1
        x = (absx + absinfo.maximum) * len(LAYOUT[0])
        x /= (absinfo.maximum * 2) + 1
        return (int(x), int(y))

    # Map a physical key to a key of the virtual keyboard depending on the current
    # value of ABS_HAT0{X,Y}. If ABS_HAT0 isn't used send the `fallback_key`.
    # `ki` corresponds to the section of the virtual keyboard to use.
    def key2vkdb(self, ev_in, ki, fallback_key):
        if ev_in.value == 0:
            return []
        elif keypos := self.vkbd_keypos(ev_in):
            key = LAYOUT[keypos[1]][keypos[0]][ki]
            return [InputEvent(key, 1), InputEvent(key, 0)]
        else:
            return [InputEvent(fallback_key, 1), InputEvent(fallback_key, 0)]

    def keyboard_map(self, ev_in):
        match ev_in.code:
            case EV_KEY.BTN_TR2:
                return [InputEvent(EV_KEY.KEY_LEFTMETA, ev_in.value)]
            case EV_KEY.BTN_DPAD_UP:
                return [InputEvent(EV_KEY.KEY_UP, ev_in.value)]
            case EV_KEY.BTN_DPAD_DOWN:
                return [InputEvent(EV_KEY.KEY_DOWN, ev_in.value)]
            case EV_KEY.BTN_DPAD_LEFT:
                return [InputEvent(EV_KEY.KEY_LEFT, ev_in.value)]
            case EV_KEY.BTN_DPAD_RIGHT:
                return [InputEvent(EV_KEY.KEY_RIGHT, ev_in.value)]
            case EV_KEY.BTN_TRIGGER_HAPPY1:
                return [InputEvent(EV_KEY.KEY_LEFTSHIFT, ev_in.value)]
            case EV_KEY.BTN_TRIGGER_HAPPY3:
                return [InputEvent(EV_KEY.KEY_LEFTCTRL, ev_in.value)]
            case EV_KEY.BTN_TRIGGER_HAPPY2:
                return [InputEvent(EV_KEY.KEY_RIGHTALT, ev_in.value)]
            case EV_KEY.BTN_TRIGGER_HAPPY4:
                return [InputEvent(EV_KEY.KEY_LEFTALT, ev_in.value)]
            case EV_KEY.BTN_SELECT:
                return [InputEvent(EV_KEY.KEY_TAB, ev_in.value)]
            case EV_KEY.BTN_START:
                return [InputEvent(EV_KEY.KEY_DELETE, ev_in.value)]
            case EV_KEY.BTN_BASE:
                return [InputEvent(EV_KEY.KEY_COMPOSE, ev_in.value)]
            case EV_ABS.ABS_Y:
                return self.joy2keys(ev_in, EV_KEY.KEY_PAGEUP, EV_KEY.KEY_PAGEDOWN)
            case EV_ABS.ABS_X:
                return self.joy2keys(ev_in, EV_KEY.KEY_HOME, EV_KEY.KEY_END)
            case EV_KEY.BTN_SOUTH:
                return self.key2vkdb(ev_in, 0, EV_KEY.KEY_ENTER)
            case EV_KEY.BTN_EAST:
                return self.key2vkdb(ev_in, 1, EV_KEY.KEY_ESC)
            case EV_KEY.BTN_NORTH:
                return self.key2vkdb(ev_in, 2, EV_KEY.KEY_BACKSPACE)
            case EV_KEY.BTN_WEST:
                return self.key2vkdb(ev_in, 3, EV_KEY.KEY_SPACE)
            case _:
                return []

    def trackpad_map(self, ev_in):
        match ev_in.code:
            case EV_KEY.BTN_TL:
                return [InputEvent(EV_KEY.BTN_RIGHT, ev_in.value)]
            case EV_KEY.BTN_TR:
                return [InputEvent(EV_KEY.BTN_LEFT, ev_in.value)]
            case EV_KEY.BTN_TL2:
                return [InputEvent(EV_KEY.BTN_MIDDLE, ev_in.value)]
            case EV_ABS.ABS_HAT1X:
                return self.abs2rel(ev_in, EV_REL.REL_X, 0.01)
            case EV_ABS.ABS_HAT1Y:
                return self.abs2rel(ev_in, EV_REL.REL_Y, -0.01)
            case _:
                return []

    def meta_map(self, ev_in):
        # switch between keyboard+mouse mode and gamepad mode
        if ev_in.value and self.cache_in[EV_KEY.BTN_MODE]:
            self.kbd_mode = not self.kbd_mode
            if self.kbd_mode:
                self.dev_in.grab()
            else:
                self.dev_in.ungrab()

    def send_sync(self, dev, events):
        dev.send_events(events + [InputEvent(EV_SYN.SYN_REPORT, 0)])

    def run(self):
        while ev_in := next(self.dev_in.events()):
            self.meta_map(ev_in)
            if self.kbd_mode:
                self.send_sync(self.dev_kbd, self.keyboard_map(ev_in))
                self.send_sync(self.dev_trackpad, self.trackpad_map(ev_in))
            self.cache_in[ev_in.code] = ev_in.value

if __name__ == '__main__':
    SDMap().run()
