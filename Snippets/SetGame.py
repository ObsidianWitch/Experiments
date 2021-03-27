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

options = { 'letter':'ABC',
            'number': (1, 2, 3),
            'color': (1, 2, 3),
            'emphasis': (curses.A_NORMAL, curses.A_BOLD, curses.A_UNDERLINE), }
deck = list( dict(zip(options.keys(), values))
             for values in itertools.product(*options.values()) )
random.shuffle(deck)
print(deck) # DEBUG
