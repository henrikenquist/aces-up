# Aces Up

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

# Intention
To explore which strategy (combination and order of move rules) has the best odds of winning the game.

# Running the code  

## Single game  

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

## Batch of games  
Only unique solutions are stored in the database.  

### Definitions
- Solution: a unique combination of deck and moves  
- Deck: a unique sequence of cards (i.e. a shuffled deck)  
- Move: [card, from_pile, to_pile, rule, move_count]  

### Main program
main.py

### Requirements
- sqlite3
- matplotlib (not critical for solving the game)
- numpy (not critical; used for predicting runtime)


### Settings

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

### User input at runtime
- Rule list (eg: 2 1 10 100 1000).
- Use new decks (number of decks) or decks stored in database (deck ids, eg: 1 2 5).

                           

# Automate strategy generation
Strategies can be generated automatically from a given rule list.

The two settings can be used in combination.  
If both are True, all subsets of rule list are permuted.  

## USE_SUB_SETS
Run games for all subsets of rule list.  

[1,20,300] -> [ [1], [1,20], [1,20,300] ]  

## PERMUTE  
Run games for all permutations of rule list.  

[1,20,300] -> [ [1,20,300], [1,300,20], [300,1,20], [20,1,300], [20,300,1], [300,20,1] ... ]  
  

## Number of games
For one deck and n rules:  

| Setting | Number of games |
|------|-----------------|
|USE_SUB_SETS = True| n |  
|PERMUTE = True| n! |  
|Both = True| n! + (n-1)! + (n-2)! + ... + 1 |   

Example:
- USE_SUB_SETS = True
- PERMUTE = True
- 8 rules
- -> 45 512 games for each deck.    


# Strategy rules         
 

## Evaluation order
Rules in strategy (rule list) are evaluated in order.  

Examples of different strategies:
 - strategy = [1,300]
 - strategy = [300, 1]
 
After a move (and following discards), rules are evaluated from beginning of the list in the next round.   
In other words, as soon as a move has been made, the following rules in the strategy are ignored (i.e. never evaluated) during that particular round.  

Example:    
 - strategy = [200, 1000]
 - rule 1000 is never reached since 200 always guarantees a move  

NOTE:
- Order of rules in list only matters if PERMUTE is set to False  
- Duplication of a rule doesn't change the strategy  

## Rules
### Group A
 1: ACE_MAX (ace from pile with largest card sum)  
 2: ACE_HAS_SUIT_BELOW (reveal card of same suit; NOTE doesn't guarantee a move)  
 3: ACE_FROM_SMALLEST (ace from smallest pile)  
 4: ACE_FROM_LARGEST (ace from largest pile)  
 5: FIRST_ACE (ace from first pile)  

### Group B
NOTE: B-rules don't guarantee a move  

 10: FROM_SMALLEST_HAS_HIGHER_IN_SUIT_BELOW (reveal higher card of same suit from smallest pile  
 20: FROM_LARGEST_HAS_HIGHER_IN_SUIT_BELOW (reveal higher card of same suit from largest   

### Group C                                         
 100: HIGHEST_HAS_HIGHER_IN_SUIT_BELOW (highest card which reveals higher card of same suit; NOTE doesn't guarantee a move)  
 200: HIGHEST_CARD (highest card from any pile)  
 300: HIGHEST_FROM_SMALLEST (highest card from smallest pile)  
 400: HIGHEST_FROM_LARGEST (highest card from largest pile)  

### Group D                                         
 1000: ANY_FROM_MAX_RANK_SUM (any card from pile with largest card sum)  



# Example results

 
Since the number of unique decks is 52! (~8x10<sup>67</sup>), the number of games needed for each strategy to get a good estimate of the odds is also probably quite large. I haven't done the math, but neither did Stanislaw Ulam who instead turned to John von Neumann who ran simulations on the ENIAC - and voilà! Monte Carlo simulations were born.  
https://permalink.lanl.gov/object/tr?what=info:lanl-repo/lareport/LA-UR-88-9068   

NOTE: Running more strategies using a deck which has a solution for one strategy will mess up the odds. This is the case since it is likely that such a deck can be solved in more than one way.  
  
The following table is created using sample code in sandbox.py and a database containing many batch runs using a unique deck for each game, with PERMUTE and USE_SUB_SETS set to False.  

| Odds  |        Strategy                     |  Decks     | Solutions |
|-------|-------------------------------------|------------|-----------|
| 108.4 | 2,1,20,100,300,1000                 |   500 000  | 4614 |
| 109.0 | 2,1,10,100,1000                     | 1 000 000  | 9172 |
| 110.9 | 2,1,10,100,300,1000                 |   500 000  | 4510 |
| 111.0 | 2,1,100,20,1000                     |   500 000  | 4503 |
| 111.3 | 2,1,100,10,1000                     | 1 000 000  | 8987 |
| 112.5 | 2,1,10,100,400,1000                 |   500 000  | 4445 |
| 113.7 | 2,1,20,100,400,1000                 |   500 000  | 4399 |
| 121.9 | 2,3,10,100,300,1000                 |   500 000  | 4101 |
| 125.0 | 2,3,20,100,400,1000                 |   500 000  | 4001 |
| 127.7 | 2,3,20,300,1000                     |   500 000  | 3914 |
| 127.9 | 1,2,10,20,100,1000                  | 1 000 000  | 7821 |
| 129.0 | 1,10,20,100,1000                    |   500 000  | 3877 |
| 130.0 | 1,10,1000                           |   500 000  | 3847 |
| 130.0 | 1,2,10,20,100,200,1000              |   500 000  | 3845 |
| 131.2 | 1,2,10,100,300,1000                 |   500 000  | 3810 |
| 132.1 | 1,2,20,100,300,1000                 |   500 000  | 3784 |
| 132.4 | 1,2,3,4,10,20,100,200,300,400,1000  |   5000 00  | 3777 |
| 133.4 | 1,2,10,100,400,1000                 |   500 000  | 3748 |
| 136.2 | 1,2,20,100,400,1000                 |   500 000  | 3672 |
| 139.3 | 1,1000                              | 1 000 000  | 7178 |
| 151.0 | 3,2,20,100,300,1000                 |   5000 00  | 3311 |
| 156.6 | 3,2,10,100,300,1000                 |   500 000  | 3192 |
| 157.5 | 3,2,20,300,1000                     |   500 000  | 3174 |



# Tips

sandbox.py contains sample code for e.g. creating stats or reading from database.  

Use DB Browser or similar to inspect the database (https://sqlitebrowser.org/).

## Other implementations of Aces Up

Includes odds/proportion distribution for scores: https://github.com/jwnorman/aces-up

Seems to use strategy = [1, 1000]  
Wins:  
- n decks:    4 000 000
- proportion: 0.007057
- odds:       141.7
  
    
A recursive(?) OO-implementation: https://github.com/magnusbakken/aces-up

# Disclaimer
This is my first Python project ever and I've been using Aces-Up as a way to learn the Python language itself, various related conventions and styles, OO-programming, Markdown, and so forth - quite a mouthful.  
Hence, it is by no means the most elegant, efficient and 'pythonic' code out there. Rather, it's a playground and hopefully an incrementally less messy learning experiment (which might be reflected in the code evolution as seen in the commits).  

As always, the TODO-list will perservere...