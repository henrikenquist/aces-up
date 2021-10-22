import cards
from itertools import accumulate

class Pile:
    def __init__(self, index):
        self.index = index
        self.cards = []

        self._repr_cache = None
        self._str_cache = None
        self._name_cache = None
    
    def __repr__(self):
        if not self._repr_cache:
            self._repr_cache = 'Pile ({self.index})'
        return self._repr_cache

    def __str__(self):
        if not self._str_cache:
            self._str_cache = self.index
        return self._str_cache

    def __name__(self):
        if not self._name_cache:
            self._name_cache = 'Pile ({self.index})'
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


# ------------- Helper methods -------------

    def length(self):
        """ Return number of cards in pile.
            Return 0 if pile is empty
        """
        return len(self.cards)


    def card_sum(self):
        """ Return sum of card ranks in pile.
        """
        card_sum = sum([e.rank for e in range(len(self.cards)) if e])
        return card_sum


    def can_move(self):
        """ Return True if number of cards in pile > 1.
            Return False if number of cards in pile <= 1.
        """

        return self.length() > 1


    def add_card(self, card):
        """ Append card to pile.
        """
         
        self.cards.append(card)


    def pop_card(self):
        """ Remove last card in pile. """

        # TODO: raise Exception if length < 0
        if self.length() > 0:
            return self.cards.pop()
        # else:
        #     raise Exception


    def last_card(self):
        """ Return last card in pile.
            Return [] is pile is empty.
        """

        if self.cards:
            return self.cards[-1]
        else:
            return []


    def last_is_ace(self):
        """ Return True if last card is an ace.
            Return False if pile is empty.
        """

        if self.last_card():
            return self.last_card().rank == cards.Rank(14)
        else:
            return False


    def has_suit_below(self):
        """ Return True if last card has card of same suit below.
            Return False if pile has less than two cards.
        """

        if self.length() > 1:
            return self.cards[-1].suit == self.cards[-2].suit
        else:
            return False


    def below_is_higher(self):
        """ Return True if last card has higher card below.
            Return False if pile has less than two cards.
        """

        if self.length() > 1:
            return self.cards[-1].rank < self.cards[-2].rank
        else:
            return False
    
    
    def is_highest_rank(self, current_row):
        """ Return True if last card in pile is largest in current row.
            Return False if pile is empty.
        """

        if self.length() > 1:
            return self.last_card >= max(current_row)
        else:
            return False


    def sum_card_ranks(self):
        """ Return sum of card ranks
        """
        card_sum = 0
        for c in self.cards:
            card_sum = card_sum + c.rank.value

        # print('card sum', card_sum)

        return card_sum