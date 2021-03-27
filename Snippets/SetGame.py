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

import itertools, random

class Game:
    TXT_RED   = '\033[91m'
    TXT_GREEN = '\033[92m'
    TXT_BLUE  = '\033[94m'
    TXT_NORMAL    = ''
    TXT_BOLD      = '\033[1m'
    TXT_UNDERLINE = '\033[4m'
    TXT_RESET = '\033[0m'

    CARD_OPTIONS = {
        'letter':'ABC',
        'number': (1, 2, 3),
        'color': (TXT_RED, TXT_GREEN, TXT_BLUE),
        'emphasis': (TXT_NORMAL, TXT_BOLD, TXT_UNDERLINE),
    }

    def __init__(self):
        self.deck = list(
            dict(zip(self.CARD_OPTIONS.keys(), values))
            for values in itertools.product(*self.CARD_OPTIONS.values())
        )
        random.shuffle(self.deck)

        self.deck, self.board = self.deck[:-12], self.deck[-12:]

    def print_board(self):
        for i, card in enumerate(self.board):
            print(f'{i}) {card["color"]}{card["emphasis"]}'
                + f'{card["letter"] * card["number"]}{self.TXT_RESET}')

    def loop(self):
        self.print_board()
        while (answer := input('>>> ')) != 'q':
            self.print_board()

Game().loop()
