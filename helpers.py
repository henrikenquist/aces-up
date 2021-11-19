import numpy as np
import matplotlib.pyplot as plt
from math import factorial
from time import strftime, gmtime
from itertools import permutations

# ____________________________________________________________________________________
#
# Read
# ____________________________________________________________________________________

def get_batch_estimates(db, number_of_decks, rule_list, PERMUTE, USE_SUB_SETS):
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
    
    runtime_sec = db.get_avg_runtime(number_of_decks) * n_games
    runtime_str = strftime("%H:%M:%S", gmtime(runtime_sec))

    return n_games, runtime_sec, runtime_str

def get_strategies(rule_list, USE_SUB_SETS, PERMUTE):
    """ Return list of strategies (list of lists or permutation objects)
    """

    strategies = [] # a list of lists

    if not USE_SUB_SETS and not PERMUTE:    # just play games with given rule list

        strategies.append(rule_list) 

    elif not USE_SUB_SETS and PERMUTE:      # permute rules in list

        strategies = permutations(rule_list, len(rule_list))

    elif USE_SUB_SETS:
    
        sub_rule_list = []

        for i,_ in enumerate(rule_list):

            sub_rule_list = rule_list[0:i+1] # NOTE: don't use append here since it updates ALL sub sets

            if PERMUTE:
                perms = permutations(sub_rule_list, len(sub_rule_list))
                for p in perms: strategies.append(p)
            else:
                strategies.append(sub_rule_list) # [1,20,300] -> [ [1], [1,20], [1,20,300] ]

    return strategies

# ____________________________________________________________________________________
#
# Plot
# ____________________________________________________________________________________

def plot_avg_runtimes(db):
    """ Average runtimes vs cumulative numbers of decks.
        Linear regression plotted.
    """

    db_info = db.get_db_info('cum_n_decks', 'avg_runtimes')
    cum_n_decks     = db_info['cum_n_decks']
    avg_runtimes_ms = np.array(db_info['avg_runtimes']) * 1000

    plt.scatter(cum_n_decks, avg_runtimes_ms, marker='x')

    # plt.plot(np.unique(cum_n_decks), np.poly1d(np.polyfit(cum_n_decks, avg_runtimes_ms, 1))(np.unique(cum_n_decks)), color = 'k')
    plt.plot(cum_n_decks, np.poly1d(np.polyfit(cum_n_decks, avg_runtimes_ms, 1))(cum_n_decks), color = 'k')

    plt.title('Avg. runtime vs cumulative number of decks over time.')
    plt.xlabel('Cumulative number of decks')
    plt.ylabel('Avg runtime (ms)')
    lin_fit_eq = 'Linear regression:{0}'.format(np.poly1d(np.polyfit(cum_n_decks, avg_runtimes_ms, 1)))
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    left, right = plt.xlim()
    _, top = plt.ylim()
    plt.text((right-left)*0.05, top*0.9, lin_fit_eq, bbox=props)
    plt.yticks(np.arange(0, max(avg_runtimes_ms), 1))
    plt.show()


