______________________________________________________________________________

 Aces Up - Intro
______________________________________________________________________________

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


______________________________________________________________________________

 How to use the code
______________________________________________________________________________

Main program: main.py

Default values of batch settings (in main.py):

db_name             = 'aces_up_test.sqlite'
USE_SUB_SETS        = False
PERMUTE             = False
STRATEGY_PRINT_OUT  = False     # display overview info for each strategy while running
GAME_PRINT_OUT      = False     # display detailed info for each game while running

Note: Printouts increase runtime.

User input when running program:
- Rule list (ex: 2 1 10 100 1000).
- Use new decks or decks stored in database (deck ids, ex: 1 2 5).

Tips:
- sandbox.py contains boilerplate code for various tests and printouts.
- Use DB Browser or similar to inspect the database (https://sqlitebrowser.org/)

______________________________________________________________________________

 Strategy rules                                 
______________________________________________________________________________

Group A
 1: ACE_MAX                                     ace from pile with largest card sum;
 2: ACE_HAS_SUIT_BELOW                          reveal card of same suit; NOTE doesn't guarantee a move
 3: ACE_FROM_SMALLEST                           ace from smallest pile
 4: ACE_FROM_LARGEST                            ace from largest pile
 5: FIRST_ACE                                   ace from first pile

Group B                                         NOTE: B-rules don't guarantee a move
 10: FROM_SMALLEST_HAS_HIGHER_IN_SUIT_BELOW     reveal higher card of same suit from smallest pile
 20: FROM_LARGEST_HAS_HIGHER_IN_SUIT_BELOW      reveal higher card of same suit from largest pile

Group C                                         
 100: HIGHEST_HAS_HIGHER_IN_SUIT_BELOW          highest card which reveals higher card of same suit;
                                                NOTE doesn't guarantee a move
 200: HIGHEST_CARD                              highest card from any pile
 300: HIGHEST_FROM_SMALLEST                     highest card from smallest pile
 400: HIGHEST_FROM_LARGEST                      highest card from largest pile

Group D                                         
 1000: ANY_FROM_MAX_RANK_SUM                    any card from pile with largest card sum


Rules are evaluated in order.

Examples:
 strategy = [1,300]
 strategy = [300, 1]
 strategy = [3,2,1, 30,20,10, 300,200, 1000]
 
After a move (and following discards), rules are evaluated from beginning of the list. 
As soon as a move has been made, no further rules in list are checked.
This means that any rule in the list after a rule which guarantees a move is never evaluated.

Example: 
 strategy = [200, 1000]     # rule 1000 is never evaluated ('used') since 200 guarantees a move.

NOTE: Order of rules in list only matters if PERMUTE is set to False
NOTE: Duplication of a rule doesn't change the strategy



______________________________________________________________________________

 Automate testing                                 
______________________________________________________________________________


Automate testing of various strategies. Can be used in combination.

USE_SUB_SETS    = True      True: run games for all subsets of rule list
                            [1,20,300] -> [ [1], [1,20], [1,20,300] ]
PERMUTE         = True      True: run games for all permutations of rules in rule list
                            [1,20,300] -> [ [1,20,300], [1,300,20], [300,1,20],
                                             20,1,300], [20,300,1], [300,20,1] etc ]

                            if USE_SUB_SETS is True: permute all subsets of rule list

For number_of_decks = 1 and n rules:

USE_SUB_SETS: True  -> n games
PERMUTE: True       -> n! games
Both: True          -> n! + (n-1)! + (n-2)! + ... + 1 games (e.g. 8 rules runs 45 512 games)


______________________________________________________________________________

 Results
______________________________________________________________________________


The value -1 as a "from" position in the move list represents the stack



______________________________________________________________________________

Implementations from other people
______________________________________________________________________________

Simulation and probability distribution:    https://github.com/jwnorman/aces-up
Seems to use strategy = [1, 1000]
Proportion: 0.007057
Odds:       141.7

A recursive OO-implementation:              https://github.com/magnusbakken/aces-up