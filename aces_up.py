import game, strategy, cards
import time
from itertools import permutations
import collections, functools, operator
import pprint

# _______________________________________________________________________________________________________
#
#  Settings                                 
# _______________________________________________________________________________________________________

# NOTE: See strategy.py for more information

number_of_decks = 1
# rule_list       = [1,2,3,4,5, 10,20, 100,200,300,400, 1000]
# rule_list       = [1,2,3,4, 10,20, 100,200,300,400, 1000]
rule_list       = [1,2,3,4, 10,20, 100,200, 1000]

USE_SUB_SETS        = True
PERMUTE             = True
STRATEGY_PRINT_OUT  = False
GAME_PRINT_OUT      = False

# RECURSIVE       = False
# deck_from_db    = []
# _______________________________________________________________________________________________________

# Game counter
game_counts     = 0
# Statistics
results         = []  # stats for each game won

highest_score   = 0
best_strategy   = []
winning_rules   = []  # used for printing total stats after main loop finishes
total_rules     = []
strategy_list   = []
score_counts    = {}  # {score: counts}, scores of all games played, used for distribution plot
deck_counts     = {}  # {deck: counts}, scores of all games played, used for distribution plot

tic             = time.perf_counter()
start_time      = time.time()

# _______________________________________________________________________________________________________
#
#  Main loop                                 
# _______________________________________________________________________________________________________

print('\nStarting...\n')

for deck_nr in range(1, number_of_decks + 1):   # use same deck for all strategies in current main loop iteration
                                                # start counting games at 1, not 0 (for human reading)
    strategies  = strategy.get_strategies(rule_list, USE_SUB_SETS, PERMUTE)
    deck        = cards.get_stack()    
        
    for curr_strategy in strategies: # BUG when both options are True

        game_counts += 1
        curr_game = game.Game(deck, curr_strategy)
        curr_game.play_game(game_counts, deck_nr, start_time, GAME_PRINT_OUT)

        # Increment value for 'score'. Append if not in dictionary.
        # Each score is a key in dict score_counts: {score : number of games with that score}
        score_counts[curr_game.get_score()] = score_counts.get(curr_game.get_score(),0) + 1
        total_rules.append(curr_game.get_rule_counts())
        
        # Update results for current won game
        # TODO save results in sqlite3 database
        # should losing decks be stored for future reference?
        # should stats för each game be stored (or a summary like the print out?)
        if curr_game.has_won():
            deck_counts[deck_nr] = deck_counts.get(deck_nr,0) + 1
            winning_rules.append(curr_game.get_rule_counts()) # NOTE: only used for printing out stats at the end
            results.append(([deck, curr_strategy, USE_SUB_SETS, PERMUTE,
                             curr_game.get_rule_counts(), curr_game.get_moves()])) # this is what we want !!!

        # For print out of losing games
        if curr_game.get_score() > highest_score:
            highest_score = curr_game.get_score()
            best_strategy = curr_strategy
            deck_best = deck_nr

        if STRATEGY_PRINT_OUT:
            print('\n===========================================================')
            print(f'Deck: {deck_nr}  Game: {game_counts}  Strategy: {curr_strategy}')


# All loops are finished
toc= time.perf_counter()


# _______________________________________________________________________________________________________
#
#  Statistics                                 
# _______________________________________________________________________________________________________

# Summary
print('\n===========================================================')
print(f'Number of wins:    {len(results)}')
print(f'Number of games:   {game_counts}')
print(f'Number of decks:   {number_of_decks}')
print(f'Proportion:        {100*len(results)/number_of_decks:0.2f} % ({len(results)/number_of_decks:0.6f})')
if len(results) > 0:
    print(f'Odds:              {number_of_decks/len(results):0.2f}')
print(f'Rule list:         {rule_list}')
print(f'Use sub sets:      {USE_SUB_SETS}')
print(f'Permute:           {PERMUTE}')
print(f'Elapsed time:      {toc - tic:0.2f} s (Game average: {1000*(toc - tic)/game_counts:0.2f} ms)')

# Scores
print('===========================================================')
if len(results) == 0:
    print(f'Highest score:      {highest_score}')
    print(f'Strategy:           {best_strategy}\r')
    print(f'Deck nr:            {deck_best}\r')
    print('\n')
print(f'Score distribution for {game_counts} games:\r')
print('\n')
pprint.pprint(score_counts)

# Rules
print('===========================================================')
if len(results) > 0:
    winning_rule_stats = dict(functools.reduce(operator.add, map(collections.Counter, winning_rules)))
    print(f'Winning rule counts ({sum(winning_rule_stats.values())})')
    print('\n')
    pprint.pprint(winning_rule_stats)
    print('\n===========================================================')
total_rule_stats = dict(functools.reduce(operator.add, map(collections.Counter, total_rules)))
print(f'Rule counts for {game_counts} games ({sum(total_rule_stats.values())}):')
print('\n')
pprint.pprint(total_rule_stats)

# Decks
if len(results) > 0:
    print('===========================================================')
    print(f'Wins per deck for {number_of_decks} decks:\r')
    print('\n')
    pprint.pprint(deck_counts)


print('\n===========================================================\n\n')



# https://www.geeksforgeeks.org/python-sum-list-of-dictionaries-with-same-key/
