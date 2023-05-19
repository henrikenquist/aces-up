import re
import sys
from src import batch, cards, database, game

DBNAME = "aces_up_db.sqlite"  # WARNING: CS50P sample database, do not edit
# DBNAME = "aces_up_db_production.sqlite" # WARNING: production batches only
# DBNAME = "aces_up_db_test.sqlite" # Go ahead, this is the playground!
db = database.Database(DBNAME)
RULES = [0, 1, 2, 3, 4, 10, 20, 30, 40, 100, 200, 300, 400, 800, 810, 900, 910, 1000]
DEFAULT_STRATEGY = [0]
EXIT_CODES = ["c", "e", "q", "cancel", "exit", "quit"]


def main():
    print("\nSee README for more information.\n")
    while True:
        option = game_option()
        if option == 1:
            play_single_game()
        elif option == 2:
            test_strategies()
        elif option == 3:
            run_batch()
        elif option == 4:
            batch_info()
        elif option == 5:
            show_stats()


def game_option() -> int:
    print("1 - Play one game with default or custom strategy")
    print("2 - Play different strategies for one deck")
    print("3 - Play a batch or a session of batches")
    print("4 - Batch information")
    print("5 - Strategy odds")
    print("\nq - Quit\n")
    while True:
        try:
            option = input("Select option: ")
            if option in EXIT_CODES:
                sys.exit(0)
            elif option not in ["1", "2", "3", "4", "5"]:
                raise ValueError()
            return int(option)
        except ValueError:
            print("Invalid option. Please try again.")


def play_single_game():
    print(f"Valid rules: {RULES}")
    print("Default strategy: 0\n")
    my_strategy = get_strategy()
    if my_strategy:
        score, _ = play_game(strategy=my_strategy)
        print(f"\nStrategy: {my_strategy}")
        if score == 48:
            print("You won! Congratulations!")
        else:
            print(f"Score: {score} (48 to win)\n")


def test_strategies():
    print(f"Valid rules: {RULES}")
    print("Default strategy: 0\n")
    curr_deck = cards.get_new_deck()
    while True:
        new_strategy = get_strategy()
        if new_strategy is None:
            print("\n")
            return
        score, _ = play_game(strategy=new_strategy, deck=curr_deck, print_out=False)
        print(f"\nScore: {score} (48 to win)\n")


def play_game(**kwargs):
    if "strategy" in kwargs:
        strategy = kwargs["strategy"]
    else:
        strategy = DEFAULT_STRATEGY
    if "deck" in kwargs:
        deck = kwargs["deck"]
    else:
        deck = cards.get_new_deck()
    if "print_out" in kwargs:
        print_out = kwargs["print_out"]
    else:
        print_out = True

    my_game = game.Game(deck, strategy, print_out)
    my_game.play()

    return my_game.score, deck


def run_batch():
    # Default settings
    settings = {
        "DB_NAME": DBNAME,
        "USE_SUB_SETS": False,
        "PERMUTE": False,
        "SAVE_ALL": True,
        "TRUST_RANDOM": True,
    }

    batch.run(**settings)


def get_strategy():
    while True:
        response = input("Select strategy ('return' for default): ").strip().lower()
        if response in EXIT_CODES:
            return None
        if not response:
            return DEFAULT_STRATEGY
        try:
            return check_strategy(response)
        except ValueError as err_msg:
            print(err_msg)


def check_strategy(response):
    strategy = list(map(int, re.findall(r"[\d]+", response)))
    if not strategy or not all(rule in RULES for rule in strategy):
        raise ValueError("Invalid rule(s). Please try again!\n")

    return strategy


def show_stats():
    # sort_by = 'solutions'
    # sort_by = 'decks'
    sort_by = "odds"
    min_n_decks = 1  # minimum number of decks per batch to include in stats table
    # min_n_decks = 100_000
    odds_list = db.get_strategy_stats_list(sort_by, min_n_decks)
    print(
        "\n----------------------------------------------------------------------------"
    )
    print(
        "{:<12s}{:<34s}{:>12s}{:>12s}".format("Odds", "Strategy", "Decks", "Solutions")
    )
    print(
        "----------------------------------------------------------------------------\n"
    )
    for rank in odds_list:
        print(
            "{:<12.1f}{:<34s}{:>12d}{:>12d}".format(
                rank["Odds"], str(rank["Strategy"]), rank["Decks"], rank["Solutions"]
            )
        )
    print(
        "\n----------------------------------------------------------------------------"
    )
    print(
        "{:<12s}{:<34s}{:>12s}{:>12s}".format("Odds", "Strategy", "Decks", "Solutions")
    )
    print(
        "----------------------------------------------------------------------------\n"
    )


def batch_info():
    db_info = db.get_db_info("batch_ids")
    batch_ids = db_info["batch_ids"]
    runtimes = []
    cum_n_decks = []
    running_val = 0
    print(
        "\n----------------------------------------------------------------------------"
    )
    print(
        "{:<10s}{:>12s}{:>12s}{:>12s}{:>15s}{:>12s}".format(
            "batch_id", "n decks", "n games", "runtime", "avg runtime", "cum n decks"
        )
    )
    print(
        "----------------------------------------------------------------------------\n"
    )
    for batch_id in batch_ids:
        n_decks, n_games, n_solutions, runtime = db.get_batch_info(batch_id)
        running_val += n_decks
        runtimes.append(1000 * runtime / n_games)
        cum_n_decks.append(running_val)
        print(
            "{:<10d}{:>12d}{:>12d}{:>12.1f}{:>12.1f}{:>14d}".format(
                batch_id,
                n_decks,
                n_games,
                runtime,
                1000 * runtime / n_games,
                running_val,
            )
        )
    print(
        "\n----------------------------------------------------------------------------"
    )
    print(
        "{:<10s}{:>12s}{:>12s}{:>12s}{:>15s}{:>12s}".format(
            "batch_id", "n decks", "n games", "runtime", "avg runtime", "cum n decks"
        )
    )
    print(
        "----------------------------------------------------------------------------\n"
    )


if __name__ == "__main__":
    main()
