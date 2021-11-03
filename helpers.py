import database
from math import factorial
from time import strftime, gmtime


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
    
    runtime_sec = database.get_avg_runtime(db_name) * n_games
    runtime_str = strftime("%H:%M:%S", gmtime(runtime_sec))

    return n_games, runtime_sec, runtime_str

