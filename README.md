# Table of contents

- [Goal](#goal)
- [Aces Up (the game)](#aces-up-the-game)
- [Running the software](#running-the-software)
  - [From command line](#from-command-line)
  - [From code](#from-code)
- [Strategy](#strategy)
  - [Evaluation order](#evaluation-order)
  - [Rules](#rules)
- [Automate strategy generation](#automate-strategy-generation)
- [Example results](#example-results)
- [Tips](#tips)
- [Requirements](#requirements)
- [Disclaimer](#disclaimer)
- [License](#license)

# Goal

To explore which strategy (combination and order of move rules) has the best odds of winning the game of Aces Up (Idiots Delight).

# Aces Up (the game)

1.  Deal four cards in a row face up.
2.  If there are two or more cards of the same suit, discard all but  
    the highest-ranked card of that suit.  
    Aces rank high.

3.  Repeat step 2 until there are no more pairs of cards with the same suit.
4.  Whenever there are any empty spaces, you may choose the top card of  
    another pile to be put into the empty space.  
    After you do this, go to Step 2.

5.  When there are no more cards to move or remove,  
    deal out the next four cards from the stack face-up onto each pile.

6.  Repeat Step 2, using only the visible, or top, cards on each of the four piles.

7.  When the last four cards have been dealt out and any moves made, the game is over.  
    The fewer cards left in the tableau, the better.  
    To win is to have only the four aces left.

When the game ends, the number of discarded cards is your score.

The maximum score (and thus the score necessary to win) is 48, which means all cards  
have been discarded except for the four aces, thus the name of the game.

Source: https://en.wikipedia.org/wiki/Aces_Up

# Running the software

There are two ways of running the software:

1. From command line
2. From code (e.g. your own)

You can run a single game or multiple games in the same run (a batch).

You can automate the generation of strategies and use these in a batch.

## From command line

CD into the root folder and run `project.py` in terminal: `> python project.py`

```
See README for more information.

0. Quit
1. Play a game of Aces Up (strategy: 1 100 1000)
2. Play a game with custom strategy
3. Play a batch of games with custom strategy
4. Display win statistics (from batches)

Select option number:

```

Example for option 1 (single game using default strategy):

```
Select option number: 1
-----------------------------------------
Dealing new cards
Th 3s Js Tc    Pile size: 1 1 1 1
-----------------------------------------
Js beats 3s
Th [] Js Tc    Pile size: 1 0 1 1
-----------------------------------------
Dealing new cards
Ah As 8s 9h    Pile size: 2 1 2 2
-----------------------------------------
Ah beats 9h
Ah As 8s Tc    Pile size: 2 1 2 1
As beats 8s
Ah As Js Tc    Pile size: 2 1 1 1
As beats Js
Ah As [] Tc    Pile size: 2 1 0 1
CARD:   Ah
RULE:   move_ace_from_highest_rank_sum
Th As Ah Tc    Pile size: 1 1 1 1
Ah beats Th
[] As Ah Tc    Pile size: 0 1 1 1
-----------------------------------------
(etc)

Score: 31 (48 to win).
```

Example for option 2 (single game using custom strategy):

```
Select option number: 2
Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000

Select strategy ('return' to exit): 100 20 3  
-----------------------------------------
Dealing new cards
4s 6c Tc 3s    Pile size: 1 1 1 1
-----------------------------------------
4s beats 3s
4s 6c Tc []    Pile size: 1 1 1 0
Tc beats 6c
4s [] Tc []    Pile size: 1 0 1 0
-----------------------------------------
(etc)

Score: 40 (48 to win).
```
Example for option 3 (batch of games using custom strategy):

```
Select option number: 3
Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000

Strategy: 100 20 3
Use new decks (return) or decks from DB (input ids):  
Number of decks: 100


===========================================================
Strategy:           [100, 20, 3]
Use sub sets:       False
Permute:            False
Number of games:    100
Estimated runtime:  00:00:00 (0 s / 2.51 ms)


Continue (return) or quit (q)?

===========================================================
Start time:         15:21:56
Stop time:          15:21:56
Runtime:            00:00:00  (0 s / 2.90 ms)

===========================================================
Unique solutions:   2
Games:              100
Decks:              100
Proportion:         2.00 % (0.020000)
Odds:               50.0

===========================================================
Unique solutions per deck (2 of 100 decks)


[(37, 1), (59, 1)]

===========================================================
Score distribution for 100 games:
{23: 1,
24: 1,
26: 3,
27: 2,
28: 1,
29: 6,
30: 5,
31: 1,
32: 1,
33: 9,
34: 4,
35: 14,
36: 5,
37: 5,
38: 6,
39: 12,
40: 6,
41: 5,
42: 6,
44: 2,
45: 1,
46: 1,
47: 1,
48: 2}

===========================================================
Rule counts for 2 solutions (15 moves)


[('move_highest_has_higher_in_suit_below', 11), ('move_ace_from_smallest', 4)]

===========================================================
Rule counts for 100 games (298 moves)


[('move_highest_has_higher_in_suit_below', 182),
('move_ace_from_smallest', 116)]

===========================================================
```

## From code

### Single game

Example:

```
from src import game, cards

deck = cards.get_new_deck()
strategy = [1, 100, 1000]
GAME_PRINT_OUT = True

my_game = game.Game(deck, strategy, GAME_PRINT_OUT)
my_game.play()

print(f"Score: {my_game.score} (48 to win).")
```

### Batch of games

Only unique solutions are stored in the database.

#### Definitions

- Solution: a unique combination of deck and moves
- Deck: a unique sequence of cards (i.e. a shuffled deck)
- Move: [card, from_pile, to_pile, rule, move_count]

#### Main program

In `main.py` you find example code for running batches of games.

#### Settings

```
# main.py

db_name = 'aces_up.sqlite'

# Strategy generation
USE_SUB_SETS        = False
PERMUTE             = False

# Console logging
STRATEGY_PRINT_OUT  = False # display overview info for each strategy at runtime
GAME_PRINT_OUT      = False # display detailed info for each game at runtime
```

Note: Printouts increase runtime.

#### User input at runtime

- Strategy (eg: 2 1 10 100 1000).
- Use new decks (number of decks) or decks stored in database (deck ids, eg: 1 2 5).

# Strategy

## Evaluation order

Rules in strategy are evaluated in order.

Examples of different strategies:

- strategy = [1,300]
- strategy = [300, 1]

After a move (and following discards), rules are evaluated from beginning of the list in the next round.  
In other words, as soon as a move has been made according to a rule, trailing rules in the strategy are ignored (i.e. never evaluated) during that particular round.

Example:

- strategy = [200, 1000]
- rule 1000 is never reached since 200 always guarantees a move (if a move is possible).

NOTE:

- The order of rules in a strategy only matters if PERMUTE is set to False
- Duplication of a rule in a strategy doesn't change the outcome of the strategy

## Rules

### Group A: Ones

1: ACE_MAX (ace from pile with largest card sum)  
2: ACE_HAS_SUIT_BELOW (reveal card of same suit; NOTE: doesn't guarantee a move)  
3: ACE_FROM_SMALLEST (ace from smallest pile)  
4: ACE_FROM_LARGEST (ace from largest pile)  
5: FIRST_ACE (ace from first pile)

### Group B: Tens

NOTE: B-rules don't guarantee a move

10: FROM_SMALLEST_HAS_HIGHER_IN_SUIT_BELOW (reveal higher card of same suit from smallest pile)  
20: FROM_LARGEST_HAS_HIGHER_IN_SUIT_BELOW (reveal higher card of same suit from largest pile)

### Group C: Hundreds

100: HIGHEST_HAS_HIGHER_IN_SUIT_BELOW (highest card which reveals higher card of same suit;  
NOTE: doesn't guarantee a move)  
200: HIGHEST_CARD (highest card from any pile)  
300: HIGHEST_FROM_SMALLEST (highest card from smallest pile)  
400: HIGHEST_FROM_LARGEST (highest card from largest pile)

### Group D: Thousands

1000: ANY_FROM_MAX_RANK_SUM (any card from pile with largest card sum)

# Automate strategy generation

Strategies can be generated automatically from a given rule list.

The two settings can be used in combination.  
If both are True, all subsets of rule list are permuted.

### USE_SUB_SETS

Run games for all subsets of rule list.

[1,20,300] -> [ [1], [1,20], [1,20,300] ]

### PERMUTE

Run games for all permutations of rule list.

[1,20,300] -> [ [1,20,300], [1,300,20], [300,1,20], [20,1,300], [20,300,1], [300,20,1] ... ]

### Number of games

For one deck and n rules:

| Setting             | Number of games                |
| ------------------- | ------------------------------ |
| USE_SUB_SETS = True | n                              |
| PERMUTE = True      | n!                             |
| Both = True         | n! + (n-1)! + (n-2)! + ... + 1 |

Example:

- USE_SUB_SETS = True
- PERMUTE = True
- 8 rules
- -> 45 512 games for each deck.

# Example results

Since the number of unique decks is 52! (~8x10<sup>67</sup>), the number of games needed for each strategy to get a good estimate of the odds is also probably quite large. I haven't done the math, but neither did Stanislaw Ulam who instead turned to John von Neumann who ran simulations on the ENIAC - and voilà! Monte Carlo simulations were born.  
https://youtu.be/OgO1gpXSUzU?t=56  
https://permalink.lanl.gov/object/tr?what=info:lanl-repo/lareport/LA-UR-88-9068

NOTE: Running more strategies using a deck which has a solution for one strategy will mess up the odds. This is the case since it is likely that such a deck can be solved in more than one way.

The following table is created using sample code in `sandbox.py` and a database containing many batch runs using a unique deck for each game, with PERMUTE and USE_SUB_SETS set to False.

| Odds  | Strategy                           | Decks     | Solutions |
| ----- | ---------------------------------- | --------- | --------- |
| 108.4 | 2,1,20,100,300,1000                | 500 000   | 4614      |
| 109.0 | 2,1,10,100,1000                    | 1 000 000 | 9172      |
| 110.9 | 2,1,10,100,300,1000                | 500 000   | 4510      |
| 111.0 | 2,1,100,20,1000                    | 500 000   | 4503      |
| 111.3 | 2,1,100,10,1000                    | 1 000 000 | 8987      |
| 112.5 | 2,1,10,100,400,1000                | 500 000   | 4445      |
| 113.7 | 2,1,20,100,400,1000                | 500 000   | 4399      |
| 121.9 | 2,3,10,100,300,1000                | 500 000   | 4101      |
| 125.0 | 2,3,20,100,400,1000                | 500 000   | 4001      |
| 127.7 | 2,3,20,300,1000                    | 500 000   | 3914      |
| 127.9 | 1,2,10,20,100,1000                 | 1 000 000 | 7821      |
| 129.0 | 1,10,20,100,1000                   | 500 000   | 3877      |
| 130.0 | 1,10,1000                          | 500 000   | 3847      |
| 130.0 | 1,2,10,20,100,200,1000             | 500 000   | 3845      |
| 131.2 | 1,2,10,100,300,1000                | 500 000   | 3810      |
| 132.1 | 1,2,20,100,300,1000                | 500 000   | 3784      |
| 132.4 | 1,2,3,4,10,20,100,200,300,400,1000 | 500 000   | 3777      |
| 133.4 | 1,2,10,100,400,1000                | 500 000   | 3748      |
| 136.2 | 1,2,20,100,400,1000                | 500 000   | 3672      |
| 139.3 | 1,1000                             | 1 000 000 | 7178      |
| 151.0 | 3,2,20,100,300,1000                | 500 000   | 3311      |
| 156.6 | 3,2,10,100,300,1000                | 500 000   | 3192      |
| 157.5 | 3,2,20,300,1000                    | 500 000   | 3174      |

# Tips

### Sample code and database inspection

- `sandbox.py` contains sample code for e.g. creating stats or reading from database.
- Use DB Browser or similar to inspect the database (https://sqlitebrowser.org/).

### Other implementations of Aces Up

Includes odds/proportion distribution for scores: https://github.com/jwnorman/aces-up

Seems to use strategy = [1, 1000]  
Wins:

- n decks: 4 000 000
- proportion: 0.007057
- odds: 141.7

A recursive(?) OO-implementation: https://github.com/magnusbakken/aces-up

# Requirements

### Packages

Running a single game requires no external packages.

Running batches requires the packages listed in `requirements.txt`

- matplotlib and dependencies (for plotting expected runtime)
- numpy and dependencies (used for predicting runtime)
- pytest (used by `test_project.py`)

### Write permission

When using batches (running and extracting statistics), a sqlite3 database is required. It is created when running the first batch and updated for consecutive batch runs. The name of the database is set in `project.py`, `main.py`, and `sandbox.py` respectively (depending on the way you choose to run the software).

# Disclaimer

This is my first Python project ever and I've been using _Aces-Up_ as a way to learn the Python language itself, various related conventions and styles, OO-programming, Markdown, and so forth - quite a mouthful.  
Hence, it is by no means the most elegant, efficient and 'pythonic' code out there. Rather, it's a playground and hopefully an incrementally less messy learning experiment (which might be reflected in the code evolution as seen in the commits).

As always, the TODO-list will perservere...

# License

[MIT License](https://mit-license.org/)

Copyright (c) 2023 Henrik Enquist (GitHub: henrikenquist)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
