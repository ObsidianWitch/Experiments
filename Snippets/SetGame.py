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

    def print_board(self, stdscr):
        for i, card in enumerate(self.board):
            stdscr.addstr(
                (card["letter"] * card["number"]).ljust(3) + '\n',
                curses.color_pair(card['color']) | card['emphasis']
            )

    def loop(self, stdscr):
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)

        self.print_board(stdscr)
        while (key := stdscr.getch()) != ord('q'):
            stdscr.clear()
            self.print_board(stdscr)

    def start(self):
        curses.wrapper(self.loop)

Game().start()
