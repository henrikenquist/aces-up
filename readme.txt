_______________________________________________________________________________________________

Aces Up
_______________________________________________________________________________________________________

1.  Deal four cards in a row face up.
2.  If there are two or more cards of the same suit,
    discard all but the highest-ranked card of that suit.
    Aces rank high.

3.  Repeat step 2 until there are no more pairs of cards with the same suit.
4.  Whenever there are any empty spaces,
    you may choose the top card of another pile to be put into the empty space.
    After you do this, go to Step 2.

5.  When there are no more cards to move or remove,
    deal out the next four cards from the stack face-up onto each pile.

6.  Repeat Step 2, using only the visible, or top, cards on each of the four piles.

7.  When the last four cards have been dealt out and any moves made, the game is over.
    The fewer cards left in the tableau, the better.
    To win is to have only the four aces left.

When the game ends, the number of discarded cards is your score.

The maximum score (and thus the score necessary to win) is 48,
which means all cards have been discarded except for the four aces, thus the name of the game.

Source: https://en.wikipedia.org/wiki/Aces_Up



_______________________________________________________________________________________________________

 Strategy rules                                 
_______________________________________________________________________________________________________

Group A
 1: ACE_FROM_LARGEST                            ace from largest pile
 2: ACE_FROM_SMALLEST                           ace from smallest pile
 3: ACE_HAS_SUIT_BELOW                          reveal card of same suit;
                                                NOTE doesn't guarantee a move
 4: ACE_MAX                                     move ace from pile with largest card sum
 5: FIRST_ACE                                   ace from first pile

Group B                                         NOTE: doesn't guarantee a move
 10: FROM_LARGEST_HAS_HIGHER_IN_SUIT_BELOW      reveal higher card of same suit from largest pile
 20: FROM_SMALLEST_HAS_HIGHER_IN_SUIT_BELOW     reveal higher card of same suit from smallest pile
 30: HIGHEST_HAS_HIGHER_IN_SUIT_BELOW           highest card which reveals higher card of same suit

Group C
 100: HIGHEST_FROM_LARGEST                      highest card from largest pile
 200: HIGHEST_FROM_SMALLEST                     highest card from smallest pile
 300: HIGHEST_CARD                              first of highest possible cards;
                                                NOTE: guarantees a move if any slot is empty
 400: MAX_SUM                                   move from pile with largest card sum

NOTE: strategy = [5, 400] seems to be same as in https://github.com/jwnorman/aces-up/blob/master/idiots_delight.py

NOTE: place rules in priority order (i.e. the strategy)
NOTE: duplication of a rule doesn't change the strategy
NOTE: Alway include rule 1 and/or 2 AND rule 60

Examples:

 strategy = [1,300]
 strategy = [2,300]
 strategy = [1,2,300]
 strategy = [3,2,1, 30,20,10, 300,200,100]


______________________________________________________________________________________________________

 Results
_______________________________________________________________________________________________________


The value -1 as a "from" position in the move list represents the stack



_______________________________________________________________________________________________________

Implementations from other people
_______________________________________________________________________________________________________

Simulation and probability distribution:    https://github.com/jwnorman/aces-up
Seems to use strategy = [5, 400]
Proportion: 0.007057
Odds:       141.7

A recursive OO-implementation:              https://github.com/magnusbakken/aces-up