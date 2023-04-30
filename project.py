import re
import sys
from src import batch, cards, database, game

DBNAME = "aces_up_db.sqlite"
db = database.Database(DBNAME)
RULES = [1, 2, 3, 4, 5, 10, 20, 100, 200, 300, 400, 1000]
DEFAULT_STRATEGY = [1, 100, 1000]
EXIT_CODES = ["n", "no", "q", "quit", "exit"]


def main():
    print("\nSee README for more information.\n")
    option = game_option()
    if option == 1:
        score, _ = play_game(strategy=get_strategy())
        print(f"\nScore: {score} (48 to win)")
    elif option == 2:
        test_strategies()
    elif option == 3:
        run_batch()
    elif option == 4:
        show_stats()


def game_option() -> int:
    print("0. Quit")
    print("1. Play one game with custom or default strategy (1 100 1000)")
    print("2. Test different strategies for one game (i.e. the same deck)")
    print("3. Play a batch of games")
    print("4. Display strategy odds (won games, from batches only)\n")
    while True:
        try:
            option = int(input("Select option number: "))
            if option == 0:
                sys.exit(0)
            elif option not in [1, 2, 3, 4]:
                raise ValueError()
            return option
        except ValueError:
            print("Invalid option. Please try again.")


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
    print("Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000\n")
    # Strategy generation
    USE_SUB_SETS = False
    PERMUTE = False
    # Console logging
    STRATEGY_PRINT_OUT = False
    GAME_PRINT_OUT = False

    # sub_sets = input("Use sub sets (y/n)? ")
    # if sub_sets == "y":
    #     USE_SUB_SETS = True
    # permutation = input("Use permutations (y/n)? ")
    # if permutation == "y":
    #     PERMUTE = True

    batch.run([DBNAME, USE_SUB_SETS, PERMUTE, STRATEGY_PRINT_OUT, GAME_PRINT_OUT])


def test_strategies():
    deck = cards.get_new_deck()
    print("Valid rules: 1 2 3 4 5 10 20 100 200 300 400 1000")
    print("Default strategy: 1 100 1000\n")
    while True:
        score, _ = play_game(strategy=get_strategy(), deck=deck, print_out=False)
        print(f"\nScore: {score} (48 to win)\n")


def get_strategy():
    while True:
        response = input(
            "Select strategy ('return' for default, 'q' to quit): "
        ).strip()
        if response in EXIT_CODES:
            sys.exit(0)
        elif not response:
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
