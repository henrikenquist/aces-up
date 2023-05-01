# Table of contents

- [Aim](#aim)
- [Aces Up (the game)](#aces-up-the-game)
- [Terminology](#terminology)
- [Running the software](#running-the-software)
  - [Using project.py](#using-projectpy)
  - [Single game using code](#single-game-using-code)
  - [Batch of games using code](#batch-of-games-using-code)
- [Strategy](#strategy)
  - [Evaluation order](#evaluation-order)
  - [Rules](#rules)
  - [Recommendations](#recommendations)
- [Automate strategy generation](#automate-strategy-generation)
- [Example results](#example-results)
- [Requirements](#requirements)
- [Disclaimer](#disclaimer)
- [Regrets and refactoring](#regrets-and-refactoring)
- [License](#license)

---

# Aim

To explore which strategy (combination and order of move rules) has the best odds of winning the game of _Aces Up_ (_Idiots Delight_).

---

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

---

# Terminology

| Term     | Definition                                                        |
| -------- | ----------------------------------------------------------------- |
| Rule     | Instruction on which card should be moved to empty pile           |
| Strategy | A sequence of rules ordered by priority                           |
| Deck     | A unique sequence of cards (i.e. a specific shuffled deck)        |
| Game     | One game _Aces Up_ using one deck and one strategy                |
| Move     | One move, defined by [card, from_pile, to_pile, rule, move_count] |
| Solution | A unique combination of deck and winning sequence of moves        |

---

# Running the software

The most simple form of playing a game consists of one deck and the default strategy (1 100 1000).

The most complex form of playing involves many decks, each of which are played using each of the auto-generated strategies, which in turn are based on your custom list of rules.

The latter is the most fun but might challenge both your CPU-fans and your patience (wait for the beep, Windows only).

### Video demo

You can [watch a demo](YouTube url goes here) on how to run the software.

### Persistence

Only information regarding won batch games are stored in the database.

Tables:
- Batches

- Decks

- Moves

- Solutions

- Strategies

### Tips

- Think through your strategies before doing anything large scale.
- Systematically build the database over time to get more reliable odds.
- Use [DB Browser](https://sqlitebrowser.org/) or similar to inspect the database.
- It could be reasonable to run a batch for only one deck, especially if USE_SUB_SETS and/or PERMUTE are used to generate strategies, or if you want to store won games.
- It is possible to run consecutive batches for one or more strategies and re-use deck(s) from previous won games (batches). By doing so, you can test new strategies for deck(s) you know can be solved.
Note: Running more strategies using a deck which has a solution for one strategy will mess up the odds. This is the case since it is likely that such a deck can be solved in more than one way. Use a separate database for such experiments (which you should try, of course!).

### Explore the unknown

If that isn't enough for you, please go ahead and adapt the code to meet your needs and expand the functionality however you like (see `sandbox.py` for sample code and license below).

Feel free to [contact me](https://github.com/henrikenquist) if you have used the code and want to collaborate, share improvements or additions, or if you have statistics from more strategies or larger batches.

### Other implementations of Aces Up

Includes odds/proportion distribution for scores: https://github.com/jwnorman/aces-up

Seems to use logic similar to strategy = [1, 1000]  
Wins:

- n decks: 4 000 000
- proportion: 0.007057
- odds: 141.7

A recursive(?) OO-implementation: https://github.com/magnusbakken/aces-up

## Using project.py

The command line user interface in `project.py` is intended to showcase the various features of the software. Not all features are available in every game option, e.g. game and strategy print-outs are disabled in options 2 and 3 in order to avoid *"console clutter"*.

With `project.py` you can:
- run a single game or a batch of games
- use new deck(s) or deck(s) from a previously won game(s) \*
- use one strategy (default or custom) or many auto-generated strategies
- show statistics of won games (from batch runs only)

\* Only available for previous batches of won games. You need to know the deck_ids for this feature.

CD into the root folder and run in terminal: `> python project.py`

```
See README for more information.

1 - Play one game with custom or default strategy (1 100 1000) 
2 - Play different strategies for one game (i.e. the same deck)
3 - Play a batch of games
4 - Display strategy odds (won games, from batches only)       

q - Quit

Select option:
```

### Example option 1 - Play one game with custom or default strategy (1 100 1000)

```
Select option number: 1
Select strategy ('return' for default, 'q' to quit):
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

Score: 31 (48 to win)
```

### Example option 2 - Test different strategies for one game (i.e. the same deck)

```
Select option number: 2
Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000
Default strategy: 1 100 1000

Select strategy ('return' for default, 'q' to quit): 2 1

Score: 31 (48 to win)

Select strategy ('return' for default, 'q' to quit): 2 1000

Score: 48 (48 to win)
```

### Example option 3a - Play a batch of games with a custom strategy

```
Select option number: 3
Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000

Strategy: 100 20 3
Use sub sets (y/n)? n
Use permutations (y/n)? n
Use new decks ('return') or decks from DB (input ids): 
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

### Example option 3b - Play a batch of games with a auto-generated strategies

```
Select option number: 3
Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000

Strategy/rule list: 5 1 200 400 1000 
Use sub sets (y/n)? y
Use permutations (y/n)? y
Use new decks ('return') or decks from DB (input ids):  
Number of decks: 1000


===========================================================
Rule list:          [5, 1, 200, 400, 1000]
Use sub sets:       True
Permute:            True
Number of games:    153000
Estimated runtime:  00:08:34 (515 s / 3.36 ms)


Continue ('return') or quit ('q')?
```

### Example option 4 - Display strategy odds (won games, from batches only)

```
Select option number: 4

----------------------------------------------------------------------------
Odds        Strategy                                 Decks   Solutions
----------------------------------------------------------------------------

62.5        1,100,1000                                 500           8
62.5        100,20,3                                   500           8
125.0       1,100,200,1000                             500           4
125.0       4,10,300,1000                              500           4

----------------------------------------------------------------------------
Odds        Strategy                                 Decks   Solutions
----------------------------------------------------------------------------
```

## Single game using code

```
from src import game, cards

deck = cards.get_new_deck()
strategy = [1, 100, 1000]
GAME_PRINT_OUT = True

my_game = game.Game(deck, strategy, GAME_PRINT_OUT)
my_game.play()

print(f"Score: {my_game.score} (48 to win).")
```

## Batch of games using code

```
from src import batch

def main():
    db_name = "aces_up.sqlite"

    # Strategy generation
    USE_SUB_SETS = False
    PERMUTE = False
    # Console logging
    STRATEGY_PRINT_OUT = False
    GAME_PRINT_OUT = False

    batch.run([db_name, USE_SUB_SETS, PERMUTE, STRATEGY_PRINT_OUT, GAME_PRINT_OUT])

if __name__ == "__main__":
    main()
```

Note: Print-outs increase runtime. Especially GAME_PRINT_OUT, which also clutters the output for batch runs.

---

# Strategy

## Evaluation order

Rules in a strategy are evaluated in order.

Examples of different strategies:

- strategy = 1 300
- strategy = 300 1

After a deal (and following discards), rules are evaluated from the beginning of the list. As soon as a move has been made according to a rule, trailing rules in the strategy are ignored (i.e. never evaluated) during that particular round. Thus, e.g. duplication of a rule in a strategy doesn't change the outcome of the strategy.

Example:

- strategy = [200, 1000]
- rule 1000 is never reached since 200 always guarantees a move (if a move is possible).

## Rules

This list of rules is by no means exhaustive. I can think of other rules I would like to include, but haven't had the time to do. Maybe you can do it and send me the code?

One example of an additional (and in hindsight, obvious) rule concept could be:

- move a card which the reveals the lowest possible card of the same suit (would be rules 30, 40 etc)

This rule concept would prioritize elimination of lower cards.

The rules are implemented in `strategy.py`. 

| Rule         | Move ...                                            |
| ------------ | --------------------------------------------------- |
| Ace          |                                                     |
| 1            | ... ace from pile with largest card sum             |
| 2 *          | ... ace with card of same suit below                |
| 3            | ... ace from smallest pile                          |
| 4            | ... ace from largest pile                           |
| 5            | ... ace from first pile                             |
| Pile size    |                                                     |
| 10 *         | ... from smallest pile with card of same suit below |
| 20 *         | ... from largest pile with card of same suit below  |
| Highest card |                                                     |
| 100 *        | ... highest card with card of same suit below       |
| 200          | ... highest card from any pile                      |
| 300          | ... highest card from smallest pile                 |
| 400          | ... highest card from largest pile                  |
| Max rank     |                                                     |
| 1000         | ... any card from pile with largest card sum        |
|              |                                                     |

\* Rules 2, 10, 20, and 100 don't guarantee a move.


## Recommendations

I would recommend that you design your strategy based on the following principles:

1. First, include one *Ace* rules somewhere. Add an extra after rule 2 if used.
2. Then, if you use a *suit below* rule (\*), add a rule that guarantees a move later in the list.
3. Finally, be creative but clever.
4. Remember that rule evaluation starts with the first rule after each deal/discard.

- Good form: 2 1 10 200
- Bad form: 2 10 100
- Good form: 400 3
- Bad form: 300 3
- Really bad form: 1 2 3 10 20 300 400 1000
- Best form? Well, that is what it's all about. You tell me!

---

# Automate strategy generation

Strategies can be generated automatically from a given rule list. All these generated strategies are then used in the batch run. This is a convenient way to test multiple strategies for any given deck and see if it is possible to win that particular game at all.

The optimal solution would be a recursive algorithm, but that is practically only possible for a very limited number of rules in a strategy due to memory restrictions. At least on my crappy old laptop.

The two settings can be used in combination. If both are `True`, all subsets of rule list are permuted.

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
|                     |                                |

Example:

- USE_SUB_SETS = True
- PERMUTE = True
- 8 rules
- -> 45 512 games for each deck.

---

# Example results

Since the number of unique decks is 52! (~8x10<sup>67</sup>), the number of games needed for each strategy to get a good estimate of the odds is also probably quite large. I haven't done the math, but neither did Stanislaw Ulam who instead turned to John von Neumann who ran [simulations on the ENIAC](https://permalink.lanl.gov/object/tr?what=info:lanl-repo/lareport/LA-UR-88-9068) - and voilà! [Monte Carlo simulations](https://youtu.be/OgO1gpXSUzU?t=56) were born.  

Note: Running more strategies using a deck which has a solution for one strategy will mess up the odds. This is the case since it is likely that such a deck can be solved in more than one way.

Note: I would not recommend running strategies like in the example below if the purpose is to check which strategy is best (hmm, that sounds familiar), since many of the strategies have bad form. Take care when designing your strategies before running large batches!

Note: All decks and moves for won games in batches are stored in the database. This means that it is possible to analyze which strategies are best. The kind of table which is shown below doesn't paint the whole picture!

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
|       |                                    |           |           |

---

# Requirements

### Modules

- Running a single game requires no additional modules.

- Running batches requires `numpy`
  
Project modules are listed in `requirements.txt`.

- I installed `pytest` (used by `test_project.py`) and `numpy` (used for predicting batch runtime) and got a lot of "bonus" modules.
  
- I also installed `matplotlib` for plotting expected runtime. This module, and its "bonus" modules are not used by `project.py`, but could be used in `sandbox.py` for various purposes.

Windows users will hear a beep when a batch run is finished (using the `winsound` module). Users on other platforms will have to stare at the screen for hours to know when their mega batches are done.

If you experience a `ModuleNotFoundError`, this might be why (although I wrapped the thing in try-except-blocks).

### Write permission

When using batches (running and extracting statistics), an sqlite database is required. It is created when running the first batch and updated for consecutive batch runs. The name of the database is set in `project.py` and `sandbox.py` respectively (depending on the way you choose to run the software).

---

# Disclaimer

This is my first Python project ever and I've been using _Aces-Up_ as a way to learn the Python language itself, various related conventions and styles, OO-programming, Markdown, sqlite, git, virtual environments, VSCode, and so forth - quite a mouthful. 

Hence, it is by no means the most elegant, efficient and "pythonic" code out there. Rather, it's a playground and hopefully an incrementally less messy learning experiment (which might be reflected in the code evolution as seen in the commits). One upside is that there is plenty of room for improvement!

As always, the TODO-list will perservere...

---

# Regrets and refactoring

Would I design the software the same way again? No, certainly not. Game logic is convoluted, code is overly complicated, and the overall design follows the infamous *"...but it works"* pattern. Also, I have learned things along the way, things which would have been helpful at the beginning of the project but were more akin to magic at the time.

Any regrets? No, nothing that can't be fixed by refactoring!

Lessons learned? First of all, I would **plan** things before starting to type. Think, then do!

So, what about the future?  

Refactoring

- optimize the code; running large batches on an old laptop is takes time
- use a more object-oriented approach
- create a design which facilitates easy addition of new rules
- make the code more "pythonic" and less verbose
- use a database framework such as SQLAlchemy
- delegate logging and timers to decorators
- ... and the list goes on

New features

- web based user interface
- support for more visual, interactive, and user friendly statistics output
- present game output graphically (e.g. display card images when playing a game)
- re-play a previous won game at "human speed"
- actually let the user play the game manually (I guess some of you just wanted that)
- ... see you in CS50W  *wink wink*

---

# License

[MIT License](https://mit-license.org/)

Copyright (c) 2023 Henrik Enquist (GitHub: henrikenquist)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
