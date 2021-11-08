import game, strategy, cards, database, helpers
from datetime import timedelta
import time
from itertools import permutations
import collections, functools, operator
import pprint
from sys import exit
import winsound

# _______________________________________________________________________________________________________
#
#  Settings (see strategy.py for more information; stored in DB table 'batches')                      
# _______________________________________________________________________________________________________

number_of_decks = 1
# rule_list       = [1,2,3,4,5, 10,20, 100,200,300,400, 1000]
# rule_list       = [1,2,3,4, 10,20, 100,200,300,400, 1000]
# rule_list       = [1,2,3,4, 10,20, 100,200, 1000]
# rule_list       = [1,2, 10,20, 100,200, 1000] # 100 decks, true, true: 591 300 games
# rule_list       = [1, 10,20, 100, 1000]
rule_list       = [2,1,100,20,1000]

# db_name         = 'solutions.sqlite'
db_name         = 'aces_up_production.sqlite'

USE_SUB_SETS        = False
PERMUTE             = False
STRATEGY_PRINT_OUT  = False
GAME_PRINT_OUT      = False

# TODO
# RECURSIVE       = False
# deck_from_db    = []
# _______________________________________________________________________________________________________

# Game counter
game_counts     = 0
# Batch flag
has_saved_batch = False
# Statistics
results         = []  # stats for each game won
highest_score   = 0
best_strategy   = []
winning_rules   = []  # used for printing total stats after main loop finishes
total_rules     = []
strategy_list   = []
score_counts    = {}  # {score: counts}, scores of all games played, used for distribution plot
deck_counts     = {}  # {deck: counts}, scores of all games played, used for distribution plot


# _______________________________________________________________________________________________________
#
#  Main loop                                 
# _______________________________________________________________________________________________________

# Calculate number of games and estimated runtime
n_games, runtime_sec, runtime_str = helpers.get_batch_estimates(db_name, number_of_decks, rule_list, PERMUTE, USE_SUB_SETS)
print('\n')
if n_games > 1000 and (STRATEGY_PRINT_OUT or GAME_PRINT_OUT):
    print('WARNING: printouts will increase estimated runtime')
print(f'Rule list:          {rule_list}')
print(f'Number of games:    {n_games}')
print(f'Estimated runtime:  {runtime_str} ({round(runtime_sec)} s / {1000*runtime_sec/n_games:0.2f} ms)')
response = input('Continue (return) or quit (q)?  ')
if response == 'q': exit()

# Timer
tic             = time.perf_counter()
start_time      = time.localtime()
print('\n\n===========================================================')
print(f'Start time:     {time.strftime("%H:%M:%S", start_time)}')

# Database
database.create_db(db_name) # if not existing

# Main loop
for deck_nr in range(1, number_of_decks + 1):   # use same deck for all strategies in current main loop iteration
                                                # start counting games at 1, not 0 (for human reading)
    strategies  = strategy.get_strategies(rule_list, USE_SUB_SETS, PERMUTE)
    deck        = cards.get_stack()    
        
    for curr_strategy in strategies:

        game_counts += 1
        curr_game = game.Game(deck, curr_strategy)
        curr_game.play_game()

        # Increment value for 'score'. Append if not in dictionary.
        # Each score is a key in dict score_counts: {score : number of games with that score}
        score_counts[curr_game.get_score()] = score_counts.get(curr_game.get_score(),0) + 1
        total_rules.append(curr_game.get_rule_counts())
        
        # Update results for current won game if is unique solution
        if curr_game.has_won() and database.is_unique_solution(db_name, deck, curr_game.get_moves()):
            # terminal printout
            deck_counts[deck_nr] = deck_counts.get(deck_nr,0) + 1
            winning_rules.append(curr_game.get_rule_counts())
            results.append(([deck, curr_game.get_moves(), curr_strategy, curr_game.get_rule_counts()]))
            if not has_saved_batch:
                batch_id = database.update_batches(db_name, number_of_decks, str(sorted(rule_list)), PERMUTE, USE_SUB_SETS, n_games, runtime_sec)
                has_saved_batch = True
            rule_counts_str = str(sorted(curr_game.get_rule_counts().items(), key=lambda x:x[1], reverse=True))
            database.save_solution(db_name, deck, curr_game.get_moves(), rule_counts_str, curr_strategy, batch_id)
            if GAME_PRINT_OUT:
                print('-----------------------------------------------------------')
                print(f'Won game nr:    {game_counts}') 
                print(f'Deck nr:        {deck_nr}') 
                print(f'Strategy:       {curr_strategy}') 
                print(f'Runtime:        {time.time() - start_time:0.2f} s')
                pprint.pprint(sorted(curr_game.get_rule_counts().items(), key=lambda x:x[1], reverse=True))
                # print(curr_game.get_moves())
                # pprint.pprint(curr_game.get_moves(excludedeals=True))
                print('-----------------------------------------------------------\n')
                print('Resuming...\n')

        # Track best game so far
        if curr_game.get_score() > highest_score:
            highest_score = curr_game.get_score()
            best_strategy = curr_strategy
            best_deck = deck_nr

        if STRATEGY_PRINT_OUT:
            print('\n===========================================================')
            print(f'Deck: {deck_nr}  Game: {game_counts}  Strategy: {curr_strategy}')


# Finally
print(f'Stop time:      {time.strftime("%H:%M:%S", time.localtime())}')
toc = time.perf_counter()
elapsed_time_str = '{:0>8}'.format(str(timedelta(seconds = round(toc - tic))))
print(f'Elapsed time:   {elapsed_time_str}  ({round(toc - tic)} s / {1000*(toc - tic)/game_counts:0.2f} ms)')
if has_saved_batch:
    database.update_runtime(db_name, batch_id, (toc - tic))

winsound.Beep(2000, 1000)
# _______________________________________________________________________________________________________
#
#  Statistics                                 
# _______________________________________________________________________________________________________

# Settings
print('===========================================================')
print(f'Unique solutions: {len(results)}')
print(f'Games:            {game_counts}')
print(f'Decks:            {number_of_decks}')
if len(results) > 0:
    print(f'Proportion:       {100*len(results)/number_of_decks:0.2f} % ({len(results)/number_of_decks:0.6f})')
    print(f'Odds:             {number_of_decks/len(results):0.1f}')
print(f'Rule list:        {rule_list}')
print(f'Use sub sets:     {USE_SUB_SETS}')
print(f'Permute:          {PERMUTE}')
# https://stackoverflow.com/questions/775049/how-do-i-convert-seconds-to-hours-minutes-and-seconds

# Unique solutions
if 25 > len(results) > 0:
    print('\n===========================================================')
    print(f'Unique solutions per deck ({len(deck_counts)} of {number_of_decks} decks):')
    print('\n')
    pprint.pprint(sorted(deck_counts.items(), key=lambda x:x[1], reverse=True))
    # sorted(data.items(), key=lambda x:x[1])

# Scores
print('\n===========================================================')
if len(results) == 0:
    print(f'Highest score:     {highest_score}')
    print(f'Strategy:          {best_strategy}\r')
    print(f'Deck nr:           {best_deck}\r')
print(f'Score distribution for {game_counts} games:')
if PERMUTE:
    print('(NB: includes potential duplicates since PERMUTE = True)')
print('\n')
pprint.pprint(score_counts)
# pprint.pprint(sorted(score_counts.items(), key=lambda x:x[1], reverse=True))

# Rules
print('\n===========================================================')
if len(results) > 0:
    winning_rule_stats = dict(functools.reduce(operator.add, map(collections.Counter, winning_rules)))
    print(f'Solutions rule counts ({sum(winning_rule_stats.values())})')
    print('\n')
    pprint.pprint(sorted(winning_rule_stats.items(), key=lambda x:x[1], reverse=True))
    print('\n===========================================================')
total_rule_stats = dict(functools.reduce(operator.add, map(collections.Counter, total_rules)))
print(f'Rule counts for {game_counts} games ({sum(total_rule_stats.values())}):')
print('\n')
pprint.pprint(sorted(total_rule_stats.items(), key=lambda x:x[1], reverse=True))

print('\n===========================================================\n\n')


# https://www.geeksforgeeks.org/python-sum-list-of-dictionaries-with-same-key/


