#!/usr/bin/env python3

# https://en.wikipedia.org/wiki/Set_(card_game)
# * cards: vary in 4 features of 3 possibilities each
#   * letter: A, B, C
#   * color: red, green, blue
#   * number: 1, 2, 3
#   * emphasis: normal, bold, underline
# * set: contains 3 cards which for each feature, the feature needs to be the
#   same or different
# * board: 12 cards
# * deck: 81 cards, covers all the possible combination of features once

import itertools, random, curses

def clamp(value, min, max):
    if value < min: return min
    if value > max: return max
    return value

class Game:
    CARD_OPTIONS = {
        'letter':'ABC',
        'number': (1, 2, 3),
        'color': (1, 2, 3),
        'emphasis': (curses.A_NORMAL, curses.A_BOLD, curses.A_UNDERLINE),
    }

    def __init__(self):
        self.deck = list(
            dict(zip(self.CARD_OPTIONS.keys(), values))
            for values in itertools.product(*self.CARD_OPTIONS.values())
        )
        random.shuffle(self.deck)
        self.deck, self.board = self.deck[:-12], self.deck[-12:]

        self.cursor = 0
        self.selected = set()

    def print_board(self, stdscr):
        for i, card in enumerate(self.board):
            if self.cursor == i:
                stdscr.addstr('>')
            else:
                stdscr.addstr(' ')

            if i in self.selected:
                stdscr.addstr('*')
            else:
                stdscr.addstr(' ')

            stdscr.addstr(
                f'{(card["letter"] * card["number"]).ljust(3)}\n',
                curses.color_pair(card['color']) | card['emphasis']
            )

    def loop(self, stdscr):
        curses.curs_set(0)
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)

        self.print_board(stdscr)
        while (key := stdscr.getch()) != ord('q'):
            # update
            if key == curses.KEY_UP:
                self.cursor = clamp(self.cursor - 1, 0, len(self.board) - 1)
            elif key == curses.KEY_DOWN:
                self.cursor = clamp(self.cursor + 1, 0, len(self.board) - 1)
            elif key == ord('\t'):
                if self.cursor not in self.selected:
                    if len(self.selected) < 3:
                        self.selected.add(self.cursor)
                else:
                    self.selected.remove(self.cursor)

            # draw
            stdscr.clear()
            self.print_board(stdscr)

    def start(self):
        curses.wrapper(self.loop)

Game().start()
