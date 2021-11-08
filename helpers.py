import database
from math import factorial
import numpy as np
import matplotlib.pyplot as plt
from time import strftime, gmtime
import matplotlib.pyplot as plt


def get_batch_estimates(db_name, number_of_decks, rule_list, PERMUTE, USE_SUB_SETS):
    """ Calculate number of games and estimated runtime.
        Return n_games, runtime_sec, runtime_str
    """
    n_games   = 0
   
    if not PERMUTE and not USE_SUB_SETS:
        n_games = number_of_decks

    if not PERMUTE and USE_SUB_SETS:
        n_games = number_of_decks * len(rule_list)

    if PERMUTE and not USE_SUB_SETS:
        n_games = number_of_decks * factorial(len(rule_list))
    
    if PERMUTE and USE_SUB_SETS:
        for i,_ in enumerate(rule_list):
            n_games += factorial(len(rule_list) - i)
        
        n_games = number_of_decks * n_games
    
    runtime_sec = database.get_avg_runtime(db_name, number_of_decks) * n_games
    runtime_str = strftime("%H:%M:%S", gmtime(runtime_sec))

    return n_games, runtime_sec, runtime_str

def plot_avg_runtimes(db_name):
    """ Plot average runtimes and best linear fit.
    """

    db_info = database.get_db_info(db_name, 'batch_ids')
    batch_ids = db_info['batch_ids']

    runtimes = []
    cum_n_decks = []
    running_val = 0

    for batch_id in batch_ids:
        n_decks, n_games, runtime = database.get_batch_info(db_name, batch_id)
        running_val += n_decks
        runtimes.append(1000*runtime/n_games)
        cum_n_decks.append(running_val)

    plt.scatter(cum_n_decks, runtimes)
    plt.plot(np.unique(cum_n_decks), np.poly1d(np.polyfit(cum_n_decks, runtimes, 1))(np.unique(cum_n_decks)), color = 'k')
    plt.xlabel('Cumulative number of decks')
    plt.ylabel('Avg runtime')
    plt.show()
