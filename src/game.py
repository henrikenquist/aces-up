from src import cards, pile, strategy
from itertools import combinations


class Game:
    """Game class.
    Input: deck, rule_list
    """

    def __init__(
        self, deck: list[cards.Card], rule_list: list[int], print_out=False
    ):

        # self.original_shuffled_deck = deck[:]
        # copy, not reference; NOTE: the same deck is used for all strategies in aces_up main loop
        self.stack = deck[:]
        self.print_out = print_out
        # self.score = 0
        self.moves = []  # (card, from_pile, to_pile, move_count)
        self.rule_counts = {}  # {fcn_metod__name__: counts}

        self.strategy = strategy.Strategy(rule_list)
        self.rule_funcs = self.strategy.get_rule_funcs()

        self.piles = [pile.Pile(0), pile.Pile(1), pile.Pile(2), pile.Pile(3)]
        self.discard_pile = pile.Pile(4)
        self.DISCARD_INDEX = 4  # piles are numbered 0-3, with discard pile as 4
        self.JOKER = cards.Card(0, 1)

    # ________________________________________________________________________________________________
    #
    #  Properties
    # ________________________________________________________________________________________________

    @property
    def current_cards(self) -> list[cards.Card]:
        """Return last card in each pile. Return [] for each empty pile."""

        curr_cards = []

        for i in range(len(self.piles)):
            curr_cards.append(self.piles[i].last_card())

        return curr_cards

    @property
    def score(self) -> int:
        """Return score (number of discarded cards).
        48 is a win.
        """
        return self.discard_pile.length()

    # ________________________________________________________________________________________________
    #
    #  Play
    # ________________________________________________________________________________________________

    def play(self) -> None:
        """Play one game.
        Used in main.py
        """

        while self.stack:  # has cards left

            self._deal()  # and discard
            self._run_strategy()  # and discard until cannot move again

            # TODO: fix recursive version
            # if RECURSIVE: self.move_rec()
            # else:         self._run_strategy()

    def move(self, from_pile: int, rule_str: str) -> None:
        """Move card to first empty pile and then discard all possible cards.
        Used in strategy.py
        """

        slots = self._empty_piles()

        card_str = from_pile.last_card()
        from_pile_idx = from_pile.index
        to_pile_idx = slots[0]

        self.moves.append(
            [
                from_pile.last_card(),
                from_pile_idx,
                to_pile_idx,
                len(self.moves) + 1,
            ]
        )
        self.piles[to_pile_idx].add_card(from_pile.pop_card())

        if self.print_out:
            print(f"CARD:   {card_str}")
            print(f"RULE:   {rule_str}")
            # print(f'FROM:   {from_pile_idx+1} ({from_pile_idx})')
            # print(f'TO:     {to_pile_idx+1} ({to_pile_idx})')
            self.print_current_cards()

        self._discard()

    def _run_strategy(self) -> None:
        """Move cards using current strategy (list of rules).

        1. Test rules in strategy priority list until one move is made.
        2. Discard all possible cards.
        3. Repeat from 1 until no move can be made.
        """

        while self._piles_ok():

            # test all rules in strategy until one move is made
            for _, move_rule_fcn in enumerate(self.rule_funcs):
                # if self.print_out: print(move_rule_fcn.__name__)

                card_is_moved = move_rule_fcn(
                    self
                )  # self here represents curr_game; used in strategy.py as curr_game

                if card_is_moved:

                    self._update_rule_counts(move_rule_fcn.__name__)
                    break  # return to beginning of rule list (restart for-loop)
                    # i.e. a priority approach to the rule order: a 'strategy'

            if not card_is_moved:
                return
            # Break while loop if no rule in strategy can move (although a potential move using another rule is possible)

    def _discard(self) -> None:
        """Discard all possible cards."""

        #
        # TODO: there has to be a more elegant version (which, eg doesn't need JOKERS)
        #
        # # Find high card for each suit
        # high_card_per_suit = dict(zip(self.deck.suit_labels,
        #                               [None] * self.num_piles))
        # https://github.com/jwnorman/aces-up/blob/master/idiots_delight.py

        while True:  # has duplicate suit

            curr_cards = (
                self.current_cards
            )  # NOTE: don't mess with this since original index is needed!

            # check for suit duplicates, excluding duplicates

            curr_suits = [e.suit for _, e in enumerate(curr_cards) if e]
            duplicate_suits = [
                i for i, e in enumerate(curr_suits) if e in curr_suits[:i]
            ]

            if not any(duplicate_suits):
                break

            # replace [] with JOKER since itertools.combinations can't handle []
            # NOTE: needs the if-else at the beginning of the comprehension
            curr_cards = [
                self.JOKER if not e else e for _, e in enumerate(curr_cards)
            ]

            # Check all combinations of card comparisons (all cards in curr_cards!)
            # print(list(combinations(curr_cards, 2)))

            # NOTE: test zip version to avoid itertools.combinations
            # print(zip(curr_cards, curr_cards[1:] + curr_cards[:1]))
            # for a,b in zip(curr_cards, curr_cards[1:] + curr_cards[:1]):
            for a, b in [
                e for _, e in enumerate(list(combinations(curr_cards, 2)))
            ]:

                if (
                    not a
                    or not b
                    or a in self.discard_pile.cards  # not []
                    or b in self.discard_pile.cards  # not already discarded
                    or a.rank == self.JOKER.rank
                    or b.rank == self.JOKER.rank  # not JOKER
                ):
                    continue

                if a.beats(b):  # checks rank and suit
                    remove_card = b
                    pile_idx = curr_cards.index(b)
                    if self.print_out:
                        print(a, "beats", b)

                elif b.beats(a):
                    remove_card = a
                    pile_idx = curr_cards.index(a)
                    if self.print_out:
                        print(b, "beats", a)

                else:
                    pile_idx = -1
                    continue

                # print('Discarding from pile:', pile_idx)
                self.moves.append(
                    [
                        remove_card,
                        pile_idx,
                        self.DISCARD_INDEX,
                        len(self.moves) + 1,
                    ]
                )  # (card, from_pile, to_pile, move_count)
                self.discard_pile.add_card(self.piles[pile_idx].pop_card())
                if self.print_out:
                    self.print_current_cards()

    def _deal(self) -> None:
        """Deal new card to each pile and discard all possible cards."""
        for to_pile in range(len(self.piles)):
            move_count = len(self.moves) + 1
            self.moves.append(
                [self.stack[-1], -1, to_pile, move_count]
            )  # -1 represents the stack
            # (card, from_pile, to_pile, move_count)
            self.piles[to_pile].add_card(self.stack.pop())

        if self.print_out:
            print("-----------------------------------------")
        if self.print_out:
            print("Dealing new cards")
        if self.print_out:
            self.print_current_cards()
        if self.print_out:
            print("-----------------------------------------")

        self._discard()

    # ________________________________________________________________________________________________
    #
    #  Read
    # ________________________________________________________________________________________________

    def get_moves(self, **kwargs) -> list:
        """Return card moves.

        [card, from_pile, to_pile, move_count]

        Optional input 'excludedeals'.
        """
        if kwargs.get("excludedeals"):
            # (card, from_pile, to_pile, move_count); from_pile = -1 repr stack (a deal)
            moves_excl_deals = [e for e in self.moves if not e[1] == -1]
            return moves_excl_deals
        else:
            return self.moves

    # ________________________________________________________________________________________________
    #
    #  Validate
    # ________________________________________________________________________________________________

    def has_won(self) -> bool:
        """Return True if score is 48.
        Return False if score is not 48.
        """
        return self.score == 48

    def _piles_ok(self) -> bool:
        """Return True if any empty piles and any pile has more than one card"""

        piles_with_more_cards = [
            i for i, e, in enumerate(self.piles) if e.length() > 1
        ]

        # if self.print_out:
        #     if any(piles_with_more_cards) and any(self._empty_piles()):
        #         print('Possible piles:', piles_with_more_cards)
        #         print('Empty piles:', self._empty_piles())

        return len(piles_with_more_cards) > 0 and len(self._empty_piles()) > 0

    def _empty_piles(self) -> list[int]:
        """Return index for all empty piles"""
        # NOTE: don't use if [] since it returns [] for empty piles
        # NOTE: Using (if e) or (if e.length() == []) cause problems in other methods, eg _piles_ok())

        return [i for i, e in enumerate(self.piles) if e.length() == 0]

    # ________________________________________________________________________________________________
    #
    #  Update
    # ________________________________________________________________________________________________

    def _update_rule_counts(self, rule_name: str) -> None:
        """Increment count for a rule move"""

        # TODO: use AUTO INCREMENT in DB instead
        # Increment value. Append rule if not in dictionary
        self.rule_counts[rule_name] = self.rule_counts.get(rule_name, 0) + 1

    # ________________________________________________________________________________________________
    #
    #  Output
    # ________________________________________________________________________________________________

    def print_current_cards(self) -> None:
        """Print last card and pile size for each pile."""

        for i in range(len(self.piles)):
            print(self.piles[i].last_card(), end=" ")
        print("   Pile size:", end=" ")

        for i in range(len(self.piles)):
            print(self.piles[i].length(), end=" ")
        print("\r")

    # ________________________________________________________________________________________________
    #
    #  Recursive version (non-functional old version)
    # ________________________________________________________________________________________________

    def _move_rec(self) -> None:

        while self._piles_ok():
            for _, move_rule_fcn in enumerate(self.rule_funcs):
                if not self._piles_ok():
                    continue

                self.card_is_moved = False
                self.card_is_moved = move_rule_fcn()
                self.nr_fcn_calls += 1

            if self.card_is_moved:
                self.discard()
                self.nr_fcn_moves += 1
                old_piles = self.piles[:]  # copy, not reference!
                self.move_rec()  # go deeper i.e. start over with same rule from the beginning
                self.piles = old_piles[:]  # backtrack: restore old state

        return

    # ________________________________________________________________________________________________
    #
    #  Remove (old code)
    # ________________________________________________________________________________________________

    # def get_deck(self) -> list[cards.Card]:
    #     """Return the original shuffled deck"""
    #     return self.original_shuffled_deck

    # def get_largest_pile(self, my_list: list[int]) -> int:
    #     """Return index and list for largest pile"""
    #     # return (max(enumerate(my_list), key = lambda tup: len(tup[1])))

    # @property
    # def rule_counts(self) -> dict[str, int]:
    #     """Return rule counts."""
    #     return self.rule_counts
