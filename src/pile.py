from src import cards

# TODO: convert to dataclass ?
class Pile:
    def __init__(self, index: int):
        self.index = index
        self.cards = []

        self._repr_cache = None
        self._str_cache = None
        self._name_cache = None

    def __repr__(self):
        if not self._repr_cache:
            self._repr_cache = "Pile ({self.index})"
        return self._repr_cache

    def __str__(self):
        if not self._str_cache:
            self._str_cache = self.index
        return self._str_cache

    def __name__(self):
        if not self._name_cache:
            self._name_cache = "Pile ({self.index})"
        return self._name_cache

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.length >= other.length
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.length > other.length
        return NotImplemented

    def __le__(self, other):
        if other is None:
            pass
        if self.__class__ is other.__class__:
            return self.length <= other.length
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.length < other.length
        return NotImplemented

    # ________________________________________________________________________________________________
    #
    #  Read
    # ________________________________________________________________________________________________

    def length(self) -> int:
        """Return number of cards in pile.
        Return 0 if pile is empty
        """
        return len(self.cards)

    def last_card(self) -> cards.Card:
        """Return last card in pile.
        Return [] is pile is empty.
        """

        if self.cards:
            return self.cards[-1]
        else:
            return []

    def card_sum(self) -> int:
        """Return sum of card ranks in pile."""
        card_sum = sum([e.rank for e in range(len(self.cards)) if e])
        return card_sum

    def sum_card_ranks(self) -> int:
        """Return sum of card ranks"""
        card_sum = 0
        for c in self.cards:
            card_sum = card_sum + c.rank.value

        # print('card sum', card_sum)

        return card_sum

    # ________________________________________________________________________________________________
    #
    #  Validate
    # ________________________________________________________________________________________________

    def can_move(self):
        """Return True if number of cards in pile > 1.
        Return False if number of cards in pile <= 1.
        """

        return self.length() > 1

    def last_is_ace(self) -> bool:
        """Return True if last card is an ace.
        Return False if pile is empty.
        """

        if self.last_card():
            return self.last_card().rank == cards.Rank(14)
        else:
            return False

    def has_suit_below(self) -> bool:
        """Return True if last card has card of same suit below.
        Return False if pile has less than two cards.
        """

        if self.length() > 1:
            return self.cards[-1].suit == self.cards[-2].suit
        else:
            return False

    def below_is_higher(self) -> bool:
        """Return True if last card has higher card below.
        Return False if pile has less than two cards.
        """

        if self.length() > 1:
            return self.cards[-1].rank < self.cards[-2].rank
        else:
            return False

    def is_highest_rank(self, current_row: list[cards.Card]) -> bool:
        """Return True if last card in pile is largest in current row.
        Return False if pile is empty.
        """

        if self.length() > 1:
            return self.last_card >= max(current_row)
        else:
            return False

    # ________________________________________________________________________________________________
    #
    #  Update
    # ________________________________________________________________________________________________

    def add_card(self, card: cards.Card) -> None:
        """Append card to pile."""

        self.cards.append(card)

    def pop_card(self) -> cards.Card:
        """Remove last card in pile."""

        # TODO: raise Exception if length < 0
        if self.length() > 0:
            return self.cards.pop()
        # else:
        #     raise Exception

    # ________________________________________________________________________________________________
    #
    #  Print
    # ________________________________________________________________________________________________
