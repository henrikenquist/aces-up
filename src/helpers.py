from math import factorial
from time import strftime, gmtime
from itertools import permutations


def get_batch_estimates(
    db, number_of_decks: int, rule_list: list[int], PERMUTE: bool, USE_SUB_SETS: bool
) -> tuple[int, float, str]:
    """Calculate number of games and estimated runtime.
    Return n_games, runtime_sec, runtime_str
    """
    n_games = 0

    if not PERMUTE and not USE_SUB_SETS:
        n_games = number_of_decks

    if not PERMUTE and USE_SUB_SETS:
        n_games = number_of_decks * len(rule_list)

    if PERMUTE and not USE_SUB_SETS:
        n_games = number_of_decks * factorial(len(rule_list))

    if PERMUTE and USE_SUB_SETS:
        for i, _ in enumerate(rule_list):
            n_games += factorial(len(rule_list) - i)

        n_games = number_of_decks * n_games

    runtime_sec = db.get_avg_runtime(number_of_decks) * n_games
    runtime_str = strftime("%H:%M:%S", gmtime(runtime_sec))

    return n_games, runtime_sec, runtime_str


def get_strategies(rule_list: list[int], USE_SUB_SETS: bool, PERMUTE: bool) -> list:
    """Return list of strategies (list of lists or permutation objects)"""

    strategies = []  # a list of lists

    if not USE_SUB_SETS and not PERMUTE:  # just play games with given rule list
        strategies.append(rule_list)

    elif not USE_SUB_SETS and PERMUTE:  # permute rules in list
        strategies = permutations(rule_list, len(rule_list))

    elif USE_SUB_SETS:
        sub_rule_list = []

        for i, _ in enumerate(rule_list):
            sub_rule_list = rule_list[
                0 : i + 1
            ]  # NOTE: don't use append here since it updates ALL sub sets

            if PERMUTE:
                perms = permutations(sub_rule_list, len(sub_rule_list))
                for p in perms:
                    strategies.append(p)
            else:
                strategies.append(
                    sub_rule_list
                )  # [1,20,300] -> [ [1], [1,20], [1,20,300] ]

    return strategies
