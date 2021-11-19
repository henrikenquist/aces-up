import enum                         # https://docs.python.org/3.11/howto/enum.html
from random import shuffle, seed

class OrderedEnum(enum.Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if other is None:
            pass
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

class Suit(OrderedEnum):
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3
    SPADES = 4

SUIT_SHORT_NAMES = {
    Suit.CLUBS: 'c',
    Suit.DIAMONDS: 'd',
    Suit.HEARTS: 'h',
    Suit.SPADES: 's',
}

class Rank(OrderedEnum):
    JOKER = 0
    ACE_ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

RANK_SHORT_NAMES = {
    Rank.JOKER: '*',
    Rank.ACE_ONE: '1',
    Rank.TWO: '2',
    Rank.THREE: '3',
    Rank.FOUR: '4',
    Rank.FIVE: '5',
    Rank.SIX: '6',
    Rank.SEVEN: '7',
    Rank.EIGHT: '8',
    Rank.NINE: '9',
    Rank.TEN: 'T',
    Rank.JACK: 'J',
    Rank.QUEEN: 'Q',
    Rank.KING: 'K',
    Rank.ACE: 'A',
}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self._repr_cache = None
        self._str_cache = None
    
    def __repr__(self):
        if not self._repr_cache:
            # self._repr_cache = 'Card({}, {})'.format(self.rank, self.suit)
            self._repr_cache = RANK_SHORT_NAMES[self.rank] + SUIT_SHORT_NAMES[self.suit]
        return self._repr_cache

    def __str__(self):
        if not self._str_cache:
            self._str_cache = RANK_SHORT_NAMES[self.rank] + SUIT_SHORT_NAMES[self.suit]
        return self._str_cache

    def beats(self, other):
        """ Check if Card and other have same Suit and Card has higher Rank
        """
        return self.suit == other.suit and self.rank > other.rank

DECK = [Card(rank, suit) for rank in list(Rank) for suit in list(Suit)]


def get_new_deck():
    """ Return a shuffled deck.
    """

    temp_deck = DECK[:] # copy, not reference; NOTE: includes JOKERS which are used in itertools.combinations

    # remove JOKER and ACE_ONE
    deck = []
    for c in temp_deck:
        if not c.rank == Rank(0) and not c.rank == Rank(1):
            deck.append(c)

    seed()
    shuffle(deck)

    return deck

def get_deck_from_str(card_str):
    """ Convert card string to deck of Cards.
    """

    deck = []

    for c in card_str.split(","):
        rank = ['2','3','4','5','6','7','8','9','T','J','Q','K','A'].index(c[0]) + 2
        # rank = c[0]
        suit = ['c', 'd', 'h', 's'].index(c[1]) + 1
        deck.append(Card(Rank(rank), Suit(suit)))

    return deck