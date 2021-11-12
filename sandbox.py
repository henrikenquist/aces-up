import database, helpers
import pprint
import winsound
import numpy as np
import matplotlib.pyplot as plt

# db_name = 'aces_up_production.sqlite'
db_name = 'aces_up_test.sqlite'

db = database.Database(db_name)


# ____________________________________________________________________________________
#
# Database
# ____________________________________________________________________________________

### Database info

# db_info = db.get_db_info('n_batches', 'batch_ids')
# n_batches = db_info['n_batches']
# batch_ids = db_info['batch_ids']
# print(n_batches)
# print(batch_ids)


# ____________________________________________________________________________________
#
# Rules
# ____________________________________________________________________________________

### Solution rule counts
### Can be used to check if all rules in strategy have been evaluated.

# rule_counts = db.get_rule_counts()
# rule_counts = db.get_rule_counts(batch_id=4)
# # rule_counts = db.get_rule_counts(moves_id=1)
# rule_counts = db.get_rule_counts(strategy_id=1)
# print('\n')
# pprint.pprint(rule_counts); print('\n')
# pprint.pprint(dict(rule_counts).keys())
# pprint.pprint(dict(rule_counts).values()); print('\n')
# print(sum(dict(rule_counts).values()))


# ____________________________________________________________________________________
#
# Batches
# ____________________________________________________________________________________

### Batches info

# db_info = db.get_db_info('batch_ids')
# batch_ids = db_info['batch_ids']
# runtimes = []
# cum_n_decks = []
# running_val = 0
# print('\n----------------------------------------------------------------------------')
# print('{:<10s}{:>12s}{:>12s}{:>12s}{:>15s}{:>12s}'.format("batch_id","n decks","n games","runtime", "avg runtime", "cum n decks"))
# print('----------------------------------------------------------------------------\n')
# for batch_id in batch_ids:
#     n_decks, n_games, n_solutions, runtime = db.get_batch_info(batch_id)
#     running_val += n_decks
#     runtimes.append(1000*runtime/n_games)
#     cum_n_decks.append(running_val)
#     print('{:<10d}{:>12d}{:>12d}{:>12.1f}{:>12.1f}{:>14d}'.format(batch_id, n_decks, n_games, runtime, 1000*runtime/n_games, running_val))
# print('\n----------------------------------------------------------------------------')
# print('{:<10s}{:>12s}{:>12s}{:>12s}{:>15s}{:>12s}'.format("batch_id","n decks","n games","runtime", "avg runtime", "cum n decks"))
# print('----------------------------------------------------------------------------\n')


#### Average runtime

# print('\n')
# print(f'Average runtime: {1000 * db.get_avg_runtime():0.3f} ms')
# print('\n')
# helpers.plot_avg_runtimes(db_name)


#### Number of games and estimated total runtime for batch

# number_of_decks = 10000
# rule_list       = [2, 1, 100, 10, 1000]
# PERMUTE         = False
# USE_SUB_SETS    = False
# n_games, runtime_sec, runtime_str = helpers.get_batch_estimates(number_of_decks, rule_list, PERMUTE, USE_SUB_SETS)
# print('\n')
# print(f'Number of games:    {n_games}')
# print(f'Estimated runtime:  {runtime_str} ({round(runtime_sec)} s / {1000*runtime_sec/n_games:0.2f} ms)')
# print('\n')
# helpers.plot_avg_runtimes(db_name)


# ____________________________________________________________________________________
#
# Strategy
# ____________________________________________________________________________________

### Strategy stats list

# sort_by = 'solutions'
# sort_by = 'decks'
# sort_by = 'odds'
# min_n_decks = 1
# odds_list = db.get_strategy_stats_list(sort_by, min_n_decks)
# print('\n----------------------------------------------------------------------------')
# print('{:<12s}{:<34s}{:>12s}{:>12s}'.format("Odds","Strategy","Decks","Solutions"))
# print('----------------------------------------------------------------------------\n')
# for rank in odds_list:
#     print('{:<12.1f}{:<34s}{:>12d}{:>12d}'.format(rank["Odds"],str(rank["Strategy"]),rank["Decks"],rank["Solutions"]))
# print('\n----------------------------------------------------------------------------')
# print('{:<12s}{:<34s}{:>12s}{:>12s}'.format("Odds","Strategy","Decks","Solutions"))
# print('----------------------------------------------------------------------------\n')


### Stats for given strategy

# curr_strategy = [2,20,10,1000,1,100,200]
# n_solutions, n_decks, odds = db.get_strategy_stats(curr_strategy)
# print('\n')
# print(f'Strategy {curr_strategy} has {n_solutions} solutions using {n_decks} decks.')
# print(f'Odds: {odds:0.1f}')
# print('\n')



