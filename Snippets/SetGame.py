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

class Model:
    CARD_OPTIONS = {
        'letter': 'ABC',
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
        self.board = []
        self.deal(12)
        self.score = 0

    def deal(self, n):
        self.board += self.deck[-n:]
        self.deck = self.deck[:-n]

    # Check if `cards` constitute a set as specified in the game rules.
    def check_gameset(self, cards):
        if len(cards) != 3: return False

        for k in cards[0].keys():
            if not(
                # a == b && b == c -> a == c: only need to check against 1st element
                all(cards[0][k] == c[k] for c in cards[1:])
                # a != b && b != c !-> a != c: need to check all combinations
                or all(c1[k] != c2[k] for c1, c2 in itertools.combinations(cards, 2))
            ): return False
        return True

    # Check if the `selected` cards constitute a set as specified in the game
    # rules. If it is the case, remove them from the board and deal 3 cards.
    def handle_gameset(self, selected):
        if self.check_gameset(list(selected.values())):
            self.score += 1
            # remove elements in reverse index order to avoid reindexing problems
            for i in sorted(selected, reverse=True):
                del self.board[i]
            self.deal(3)
            return True
        return False

class Game:
    GRID_WIDTH = 3

    def __init__(self):
        self.model = Model()
        self.cursor = 0
        self.selected = dict()

    def update(self, key):
        if key == curses.KEY_LEFT:
            self.cursor -= 1
        elif key == curses.KEY_RIGHT:
            self.cursor += 1
        elif key == curses.KEY_UP:
            self.cursor -= self.GRID_WIDTH
        elif key == curses.KEY_DOWN:
            self.cursor += self.GRID_WIDTH
        self.cursor = clamp(self.cursor, 0, len(self.model.board) - 1)

        if key == ord('n'):
            self.__init__()
        elif key == ord('d'):
            self.model.deal(3)
        elif key == ord('\t'):
            if self.cursor not in self.selected:
                if len(self.selected) < 3:
                    self.selected[self.cursor] = self.model.board[self.cursor]
            else:
                del self.selected[self.cursor]
        elif key == ord('\n'):
            if self.model.handle_gameset(self.selected):
                self.selected.clear()
                if (not self.model.deck) and (not self.model.board):
                    self.__init__()

    def draw(self, stdscr):
        stdscr.clear()
        for i, card in enumerate(self.model.board):
            if self.cursor == i:
                stdscr.addstr('>')
            else:
                stdscr.addstr(' ')

            if i in self.selected:
                stdscr.addstr('*')
            else:
                stdscr.addstr(' ')

            stdscr.addstr(
                f'{(card["letter"] * card["number"]).ljust(3)}',
                curses.color_pair(card['color']) | card['emphasis']
            )
            if (i + 1) % self.GRID_WIDTH == 0:
                stdscr.addstr('\n')

        stdscr.addstr(f'\ndeck:{len(self.model.deck)} score:{self.model.score}')
        stdscr.addstr(f'\nn: new game, d: deal, q: quit')
        stdscr.addstr(f'\narrows: move cursor, tab: select card, enter: check set')

    def loop(self, stdscr):
        curses.curs_set(0)
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)

        self.draw(stdscr)
        while (key := stdscr.getch()) != ord('q'):
            self.update(key)
            self.draw(stdscr)

    def start(self):
        curses.wrapper(self.loop)

Game().start()
