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

import curses, itertools, random

class Game:
    OPTIONS = {
        'letter':'ABC',
        'number': (1, 2, 3),
        'color': (1, 2, 3),
        'emphasis': (curses.A_NORMAL, curses.A_BOLD, curses.A_UNDERLINE),
    }

    def __init__(self):
        self.deck = list(
            dict(zip(self.OPTIONS.keys(), values))
            for values in itertools.product(*self.OPTIONS.values())
        )
        random.shuffle(self.deck)

        self.deck, self.board = self.deck[:-12], self.deck[-12:]

game = Game()
print(len(game.deck), len(game.board)) # DEBUG
