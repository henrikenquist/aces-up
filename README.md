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

A specific solution can result from different strategies, since the same sequence of moves can result from different sets of rules. In other words, the same cards in a deck have been moved in the same sequence.

Such "duplicate" solutions are treated as one unique solution when stored in the database, but the link between each winning strategy and the solution is stored for future reference.

---

# Running the software

The most simple form of playing a game consists of one deck and the default strategy (rule 0, highest card).

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

### Explore the unknown and reach out

If that isn't enough for you, please go ahead and adapt the code to meet your needs and expand the functionality however you like (see `sandbox.py` for sample code and license below).

Feel free to [contact me](https://github.com/henrikenquist) if you have used the code and want to collaborate, share improvements or additions, report bugs, or if you have statistics from more strategies or larger batches. ...or to buy me a coffee!

### Other implementations of Aces Up

Includes odds/proportion distribution for scores: https://github.com/jwnorman/aces-up

Seems to use logic similar to strategy = [200, 2]  
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

You can enter rules in almost any format:
- 300 3 0
- 300,3,0
- 300-3-0
- 300/3/0
- [300 3 0]
- [300,3,0]
- ...

```
See README for more information.

1 - Play one game with custom or default strategy (0: highest card) 
2 - Play different strategies for one game (i.e. the same deck)
3 - Play a batch of games
4 - Display strategy odds (won games, from batches only)       

q - Quit

Select option:
```

### Example option 1 - Play one game with custom or default strategy (0: highest card)

```
Select option: 1
Valid rules: [0, 1, 2, 3, 4, 10, 20, 30, 40, 100, 200, 300, 400]
Default strategy: 0

Select strategy ('return' for default, 'q' to quit): 1 2
-----------------------------------------
Dealing new cards
2d 5s 3c 9c    Pile size: 1 1 1 1
-----------------------------------------
9c beats 3c
2d 5s [] 9c    Pile size: 1 1 0 1
-----------------------------------------
Dealing new cards
7c Td 8d 9s    Pile size: 2 2 1 2
-----------------------------------------
Td beats 8d
7c Td [] 9s    Pile size: 2 2 0 2
CARD:   9s
RULE:   move_highest_from_highest_rank_sum
7c Td 9s 9c    Pile size: 2 2 1 1
9c beats 7c
2d Td 9s 9c    Pile size: 1 2 1 1
Td beats 2d
[] Td 9s 9c    Pile size: 0 2 1 1
CARD:   Td
RULE:   move_highest_from_highest_rank_sum
Td 5s 9s 9c    Pile size: 1 1 1 1
9s beats 5s
Td [] 9s 9c    Pile size: 1 0 1 1

(etc)

Strategy: [1, 2]
Score: 42 (48 to win)
```

### Example option 2 - Test different strategies for one game (i.e. the same deck)

```
Select option: 2
Valid rules: [0, 1, 2, 3, 4, 10, 20, 30, 40, 100, 200, 300, 400]
Default strategy: 0

Select strategy ('return' for default, 'q' to quit):

Score: 45 (48 to win)

Select strategy ('return' for default, 'q' to quit): 2 1 0

Score: 36 (48 to win)

(etc)
```

### Example option 3a - Play a batch of games with a custom strategy

```
Select option: 3
Valid rules: [0, 1, 2, 3, 4, 10, 20, 30, 40, 100, 200, 300, 400]

Select strategy/rule list: 200 1 2
Use sub sets (y/n)? n
Use permutations (y/n)? n
Use new decks ('return') or decks from DB (input deck_ids):  
Number of decks: 500


===========================================================
Rule list:          [200, 1, 2]
Use sub sets:       False
Permute:            False
Number of games:    500
Estimated runtime:  00:00:01 (1 s / 2.52 ms)


Continue ('return') or quit ('q')?

===========================================================
Start time:         14:25:33
Stop time:          14:25:35
Runtime:            00:00:01  (1 s / 2.25 ms)

===========================================================
Unique solutions:   4
Games:              500
Decks:              500
Proportion:         0.80 % (0.008000)
Odds:               125.0

===========================================================
Unique solutions per deck (4 of 500 decks)


[(7, 1), (30, 1), (165, 1), (491, 1)]

===========================================================
Score distribution for 500 games:
{18: 1,
 22: 2,
 23: 2,
 24: 2,
 25: 6,
 26: 7,
 27: 12,
 28: 12,
 29: 14,
 30: 18,
 31: 22,
 32: 19,
 33: 22,
 34: 28,
 35: 33,
 36: 35,
 37: 47,
 38: 32,
 39: 34,
 40: 29,
 41: 24,
 42: 29,
 43: 16,
 44: 16,
 45: 17,
 46: 12,
 47: 5,
 48: 4}

===========================================================
Rule counts for 4 solutions (28 moves)


[('move_ace_from_highest_rank_sum', 14),
 ('move_highest_from_highest_rank_sum', 10),
 ('move_highest_has_higher_in_suit_below', 4)]

===========================================================
Rule counts for 500 games (2109 moves)


[('move_highest_from_highest_rank_sum', 895),
 ('move_ace_from_highest_rank_sum', 742),
 ('move_highest_has_higher_in_suit_below', 472)]

===========================================================
```

### Example option 3b - Play a batch of games with a auto-generated strategies

```
Select option: 3
Valid rules: [0, 1, 2, 3, 4, 10, 20, 30, 40, 100, 200, 300, 400]

Select strategy/rule list: 1 2 200
Use sub sets (y/n)? y
Use permutations (y/n)? y
Use new decks ('return') or decks from DB (input deck_ids):  
Number of decks: 1000


===========================================================
Rule list:          [1, 2, 200]
Use sub sets:       True
Permute:            True
Number of games:    9000
Estimated runtime:  00:00:09 (9 s / 1.00 ms)


Continue ('return') or quit ('q')?

===========================================================
Start time:         14:38:22
Stop time:          14:38:35
Runtime:            00:00:13  (13 s / 1.39 ms)

===========================================================
Unique solutions:   41
Games:              9000
Decks:              1000
Proportion:         4.10 % (0.041000)
Odds:               24.4

===========================================================
Unique solutions per deck (id) for 30 of 1000 decks.



===========================================================
Score distribution for 9000 games:
(Note: Includes potential duplicates since PERMUTE = True)


{17: 9,
 18: 1,
 19: 18,
 20: 14,
 21: 32,
 22: 28,
 23: 22,
 24: 53,
 25: 108,
 26: 175,
 27: 267,
 28: 216,
 29: 271,
 30: 291,
 31: 384,
 32: 509,
 33: 519,
 34: 520,
 35: 623,
 36: 549,
 37: 509,
 38: 595,
 39: 583,
 40: 448,
 41: 410,
 42: 448,
 43: 414,
 44: 306,
 45: 250,
 46: 209,
 47: 109,
 48: 110}

===========================================================
Rule counts for 41 solutions (297 moves)


[('move_highest_from_highest_rank_sum', 169),
 ('move_highest_has_higher_in_suit_below', 68),
 ('move_ace_from_highest_rank_sum', 60)]

===========================================================
Rule counts for 9000 games (35365 moves)


[('move_highest_from_highest_rank_sum', 23148),
 ('move_highest_has_higher_in_suit_below', 8002),
 ('move_ace_from_highest_rank_sum', 4215)]

===========================================================
```

### Example option 4 - Display strategy odds (won games, from batches only)

Results after running "Example option 3b" batch described above using an empty database, and then running a second batch using the *random* rule (1000) as strategy. 

```
Select option: 4

----------------------------------------------------------------------------
Odds        Strategy                                 Decks   Solutions
----------------------------------------------------------------------------

62.5        1,2                                       1000          16
90.9        0                                         1000          11
111.1       1000                                      1000           9
142.9       2,1                                       1000           7
142.9       1,200,2                                   1000           7
200.0       200,1,2                                   1000           5
250.0       200,2,1                                   1000           4
500.0       1                                         1000           2

----------------------------------------------------------------------------
Odds        Strategy                                 Decks   Solutions
----------------------------------------------------------------------------
```

## Single game using code

```
from src import game, cards

deck = cards.get_new_deck()
strategy = [1, 2, 0]
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

- strategy A = [1, 3]
- strategy B = [3, 1]

After a deal (and following discards), rules are evaluated from the beginning of the list. As soon as a move has been made according to a rule, trailing rules in the strategy are ignored (i.e. never evaluated) during that particular round. Thus, e.g. duplication of a rule in a strategy doesn't change the outcome of the strategy.

Example:

- strategy = [3, 300]
- rule 300 is never reached since 3 always guarantees a move (if a move is possible).

## Rules

The rules are implemented in `strategy.py`.

Rule moves card from leftmost pile if more than one card matches the rule.

Moves are only made from piles larger than one card.

| Rule         | Move ...                                         |
| ------------ | ------------------------------------------------ |
| Default      |                                                  |
| 0            | ... highest card from any pile                   |
| Highest card |                                                  |
| 1 *          | ... highest card with card of same suit below    |
| 2            | ... highest card from pile with largest card sum |
| 3            | ... highest card from smallest pile              |
| 4            | ... highest card from largest pile               |
| Lowest card  |                                                  |
| 10 *         | ... lowest card with card of same suit below     |
| 20           | ... lowest card from pile with largest card sum  |
| 30           | ... lowest card from smallest pile               |
| 40           | ... lowest card from largest pile                |
| Ace          |                                                  |
| 100 *        | ... ace with card of same suit below             |
| 200          | ... ace from pile with largest card sum          |
| 300          | ... ace from smallest pile                       |
| 400          | ... ace from largest pile                        |
| Random       |                                                  |
| 1000         | ... card from random pile                        |
|              |                                                  |

\* Rules 1, 10, and 100 don't guarantee a move.

### A friendly conversation

A player might say:
> "Hey dude, the _Ace_ rule moves are covered by the _Highest card_ rules so why not only use the latter?"

I reply:
> "That is correct, my friend. But! What if you want to test a strategy where you only want to move the aces, but not the highest card (if not an ace)?"

The player is not convinced:
> "Why would you do that? Isn't that stupid? Don't you want to win the game?"

I explain:
> "Well remember, the aim of this software is to test different strategies, so this is a feature - not a bug.
> 
> Run game option 2, first with rule 3 and then with rule 30. You will see that you (sometimes) get different scores!

### Missing rules

The list above is by no means exhaustive. I can think of other rules I would like to include, but haven't had the time to do. Maybe you can do it and send me the code?

Some examples of additional (and in hindsight, obvious) rule concepts could be:

- move the highest card which reveals the **lowest** card of the same suit
- move the lowest card which reveals the **highest** card of the same suit

This concept could prioritize elimination of lower cards better than the existing rules. The same idea goes for the other classes of rules as well.

## Recommendations

I would recommend that you design your strategy based on the following principles:

1. Place any *Ace* rule before any corresponding *Highest card* rule.
3. Place any *Suit below* (\*) rule before any other corresponding rule.
4. Add a rule that guarantees a move somewhere after *Suit below* rule (\*).
5. Remember: rule evaluation starts with the first rule after each deal/discard.
6. Remember: more rules in a strategy is **not** necessarily better.
7. Finally, be creative but clever.

Generally:
- Good form: 1 2
- Bad form: 2 1
- Good form: 300 3
- Bad form: 3 300
- Really bad form: 0 1 2 3 4 10 20 30 40 100 200 300 400 \*
- Best form? Well, that is what it's all about. You tell me!

\* Well, it is meaningful when using `SUB_SET` and/or `PERMUTE` in batches, e.g. if you want to run a really big batch (see *Number of games* below).

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

- USE_SUB_SETS = `True`
- PERMUTE = `True`
- 13 rules (i.e. all implemented rules)
- -> 6 749 977 113 [games for each deck](https://www.symbolab.com/solver/induction-calculator/solve%20for%20%5Csum_%7Bn%3D1%7D%5E%7B13%7D%20%5Cleft(n%5Cright)!?or=input).

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
- let the user set the default strategy and other settings (stored in db, text file, or cookie)
- actually let the user play the game manually (I guess some of you just wanted that)
- ... see you in CS50W  *wink wink*

---

# License

[MIT License](https://mit-license.org/)

Copyright (c) 2023 Henrik Enquist (GitHub: henrikenquist)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
