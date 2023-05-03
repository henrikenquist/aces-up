import re
import sys
from src import batch, cards, database, game

DBNAME = "aces_up_db.sqlite"  # WARNING: for CS50P project only
# DBNAME = "aces_up_db_production.sqlite"
# DBNAME = "aces_up_db_test.sqlite"
db = database.Database(DBNAME)
RULES = [0, 1, 2, 3, 4, 10, 20, 30, 40, 100, 200, 300, 400, 1000]
DEFAULT_STRATEGY = [0]
EXIT_CODES = ["c", "e", "n", "q", "cancel", "exit", "no", "quit"]


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
            show_stats()


def game_option() -> int:
    print("1 - Play one game with default or custom strategy")
    print("2 - Play different strategies for one game (deck)")
    print("3 - Play a batch of games")
    print("4 - Display strategy odds")
    print("\nq - Quit\n")
    while True:
        try:
            option = input("Select option: ")
            if option in EXIT_CODES:
                sys.exit(0)
            elif option not in ["1", "2", "3", "4"]:
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
    deck = cards.get_new_deck()
    while True:
        my_strategy = get_strategy()
        if my_strategy is None:
            print("\n")
            return
        score, _ = play_game(strategy=my_strategy, deck=deck, print_out=False)
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
    print(f"Valid rules: {RULES}\n")
    kwargs = {
        "DB_NAME": DBNAME,
        "USE_SUB_SETS": False,
        "PERMUTE": False,
        "SAVE_ALL": True,
        "TRUST_RANDOM": True,
        "STRATEGY_PRINT_OUT": False,
        "GAME_PRINT_OUT": False,
    }

    batch.run(**kwargs)


def get_strategy():
    # print(f"Valid rules: {RULES}")
    # print("Default strategy: 0\n")
    while True:
        response = input(
            "Select strategy ('return' for default, 'q' to exit): "
        ).strip()
        if response in EXIT_CODES:
            # sys.exit(0)
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
    # min_n_decks = 100_000
    min_n_decks = 1  # minimum number of decks per batch to include in stats table
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


if __name__ == "__main__":
    main()
