import database, helpers
import pprint
import winsound
import numpy as np
import matplotlib.pyplot as plt

# db_name = 'aces_up_production.sqlite'
db_name = 'aces_up_test.sqlite'

### Database info

# db_info = database.get_db_info(db_name, 'n_batches', 'batch_ids')
# n_batches = db_info['n_batches']
# batch_ids = db_info['batch_ids']
# print(n_batches)
# print(batch_ids)


### Batches info

# db_info = database.get_db_info(db_name, 'batch_ids')
# batch_ids = db_info['batch_ids']
# runtimes = []
# cum_n_decks = []
# running_val = 0
# print('\n----------------------------------------------------------------------------')
# print('{:<10s}{:>12s}{:>12s}{:>12s}{:>15s}{:>12s}'.format("batch_id","n decks","n games","runtime", "avg runtime", "cum n decks"))
# print('----------------------------------------------------------------------------\n')
# for batch_id in batch_ids:
#     n_decks, n_games, runtime = database.get_batch_info(db_name, batch_id)
#     running_val += n_decks
#     runtimes.append(1000*runtime/n_games)
#     cum_n_decks.append(running_val)
#     print('{:<10d}{:>12d}{:>12d}{:>12.1f}{:>12.1f}{:>14d}'.format(batch_id, n_decks, n_games, runtime, 1000*runtime/n_games, running_val))
# print('\n----------------------------------------------------------------------------')
# print('{:<10s}{:>12s}{:>12s}{:>12s}{:>15s}{:>12s}'.format("batch_id","n decks","n games","runtime", "avg runtime", "cum n decks"))
# print('----------------------------------------------------------------------------\n')


### Strategy stats list

# sort_by = 'solutions'
# sort_by = 'decks'
# sort_by = 'odds'
# min_n_decks = 1
# odds_list = database.get_strategy_stats_list(db_name, sort_by, min_n_decks)
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
# n_solutions, n_decks, odds = database.get_strategy_stats(db_name, curr_strategy)
# print('\n')
# print(f'Strategy {curr_strategy} has {n_solutions} solutions using {n_decks} decks.')
# print(f'Odds: {odds:0.1f}')
# print('\n')



#### Number of games and estimated total runtime for batch

# number_of_decks = 10000
# rule_list       = [2, 1, 100, 10, 1000]
# PERMUTE         = False
# USE_SUB_SETS    = False
# n_games, runtime_sec, runtime_str = helpers.get_batch_estimates(db_name, number_of_decks, rule_list, PERMUTE, USE_SUB_SETS)
# print('\n')
# print(f'Number of games:    {n_games}')
# print(f'Estimated runtime:  {runtime_str} ({round(runtime_sec)} s / {1000*runtime_sec/n_games:0.2f} ms)')
# print('\n')
# helpers.plot_avg_runtimes(db_name)



#### Average runtime from DB

# print('\n')
# print(f'Average runtime: {1000 * database.get_avg_runtime(db_name):0.3f} ms')
# print('\n')
# helpers.plot_avg_runtimes(db_name)



#### Get solution rule counts from DB

# rule_counts = database.get_rule_counts(db_name)
# print('\n')
# pprint.pprint(rule_counts)
# print(type(rule_counts))
# print('\n')
# pprint.pprint(dict(rule_counts).keys())
# pprint.pprint(dict(rule_counts).values())
# print(type(dict(rule_counts)),'\n')

