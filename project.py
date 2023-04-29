import re
import sys
from src import batch, cards, database, game

DBNAME = "aces_up_project.sqlite"
db = database.Database(DBNAME)
RULES = [1, 2, 3, 4, 5, 10, 20, 100, 200, 300, 400, 1000]


def main():
    print("\nSee README for more information.\n\n")
    option = user_input()
    if option == 1:
        print(f"\nScore: {play_game()} (48 to win).")
    elif option == 2:
        print(f"\nScore: {play_strategy()} (48 to win).")
    elif option == 3:
        run_batch()
    elif option == 4:
        show_stats()


def user_input() -> int:
    print("0. Quit")
    print("1. Play a game of Aces Up (strategy: 1 100 1000)")
    print("2. Play a game with custom strategy")
    print("3. Play a batch of games with custom strategy")
    print("4. Display win statistics (from batches)\n")
    while True:
        try:
            option = int(input("Select option number: "))
            if option == 0:
                sys.exit(0)
            elif option in [1, 2, 3, 4]:
                return option
            else:
                raise ValueError()
        except ValueError:
            print("Invalid option. Please try again.")


def play_game(*args) -> int:
    if len(args) == 1:
        strategy = args[0]
    else:
        strategy = [1, 100, 1000]
    deck = cards.get_new_deck()
    my_game = game.Game(deck, strategy, True)
    my_game.play()
    return my_game.score


def play_strategy():
    print("Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000\n")
    while True:
        try:
            response = input("Select strategy ('return' to exit): ")
            if not response:
                sys.exit(0)
            else:
                strategy = check_strategy(response)
                return play_game(strategy)
        except ValueError:
            print("Invalid game strategy. See README for more information.\n")


def check_strategy(response):
    strategy = list(map(int, re.findall(r"[\d]+", response)))
    if not all(rule in RULES for rule in strategy):
        raise ValueError
    return strategy


def run_batch():
    print("Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000\n")
    # Strategy generation
    USE_SUB_SETS = False
    PERMUTE = False
    # Console logging
    STRATEGY_PRINT_OUT = False
    GAME_PRINT_OUT = False

    batch.run([DBNAME, USE_SUB_SETS, PERMUTE, STRATEGY_PRINT_OUT, GAME_PRINT_OUT])


def show_stats():
    # sort_by = 'solutions'
    # sort_by = 'decks'
    sort_by = "odds"
    # min_n_decks = 100_000
    min_n_decks = 1
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
