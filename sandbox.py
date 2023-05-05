import numpy as np
import matplotlib.pyplot as plt
import pprint

try:
    import winsound  # windows only!
except:
    pass
from src import cards, database, game, helpers

# See project.py for more examples

# Running these functions:
#
# 1. Open terminal and navigate to Aces Up root folder.
# 2. Start Python in terminal by typing: python
# 3. Import functions, type: from sandbox import *
# 4. Run (ex.), type: play_game()

# DBNAME = "aces_up_db.sqlite"  # WARNING: CS50P sample database, do not edit
# DBNAME = "aces_up_db_production.sqlite" # WARNING: production batches only
DBNAME = "aces_up_db_test.sqlite"  # Go ahead, this is the playground!
db = database.Database(DBNAME)


def play_game():
    deck = cards.get_new_deck()
    strategy = [2, 1, 0]
    GAME_PRINT_OUT = True

    my_game = game.Game(deck, strategy, GAME_PRINT_OUT)
    my_game.play()

    print(f"Score: {my_game.score} (48 to win).")


def new_deck():
    deck = cards.get_new_deck()
    print(deck)


def deck_from_db():
    deck = db.get_deck(1)
    print(deck)


def deck_from_string():
    card_str = "Kh,Ah,As,7c,6h,4s,Jc,Qh,Tc,Ts,5s,3h,Jh,Td,3s,2d,Th,9h,4h,7d,Qd,5c,5h,Kd,Jd,Js,8s,4c,5d,2h,6c,7s,Ks,Qs,9c,7h,2c,Kc,8h,9d,Ac,6s,4d,6d,Ad,9s,2s,3c,8d,3d,8c,Qc"
    deck = cards.get_deck_from_str(card_str)
    print(deck)


def db_info():
    """Simple stats from database"""
    try:
        db_info = db.get_db_info("n_batches", "batch_ids", "cum_n_decks")
        print(db_info)
        print(db_info["n_batches"])
        print(db_info["cum_n_decks"])
    except database.NotFoundError as e:
        print(e)


def solution_rule_counts():
    """Can be used to check if all rules in strategy have been evaluated."""

    # all
    rule_counts = db.get_rule_counts()

    # Filters (set your own correct values)
    #
    # rule_counts = db.get_rule_counts(batch_id=4)
    # rule_counts = db.get_rule_counts(moves_id=1)
    rule_counts = db.get_rule_counts(strategy_id=1)

    print("\n")
    pprint.pprint(rule_counts)
    print("\n")
    pprint.pprint(dict(rule_counts).keys())
    pprint.pprint(dict(rule_counts).values())
    print("\n")
    print(sum(dict(rule_counts).values()))


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


def total_strategy_stats():
    """Stats for all strategies"""

    # Filters
    # sort_by = "solutions"
    # sort_by = "decks"
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


def plot_number_games_runtimes():
    """Number of games and estimated total runtime for batch.

    Plot and print stored average runtimes.
    Linear regression line included.
    Print estimated runtime from given settings.
    """
    number_of_decks = 10000
    rule_list = [2, 1, 100, 10, 1000]  # only the number of rules matter
    PERMUTE = False  # change to fit your needs
    USE_SUB_SETS = False  # change to fit your needs
    n_games, runtime_sec, runtime_str = helpers.get_batch_estimates(
        db, number_of_decks, rule_list, PERMUTE, USE_SUB_SETS
    )
    print("\n")
    print(f"Number of games:    {n_games}")
    print(
        f"Estimated runtime:  {runtime_str} ({round(runtime_sec)} s / {1000*runtime_sec/n_games:0.2f} ms)"
    )
    print("\n")
    plot_avg_runtimes()


def plot_avg_runtimes() -> None:
    """Average runtimes vs cumulative numbers of decks.

    Plot and print stored average runtimes.
    Linear regression line included.
    """

    db_info = db.get_db_info("cum_n_decks", "avg_runtimes")
    cum_n_decks = db_info["cum_n_decks"]
    avg_runtimes_ms = np.array(db_info["avg_runtimes"]) * 1000

    print(f"\nAverage runtime: {1000 * db.get_avg_runtime():0.3f} ms\n")

    plt.scatter(cum_n_decks, avg_runtimes_ms, marker="x")

    # plt.plot(np.unique(cum_n_decks), np.poly1d(np.polyfit(cum_n_decks, avg_runtimes_ms, 1))(np.unique(cum_n_decks)), color = 'k')
    plt.plot(
        cum_n_decks,
        np.poly1d(np.polyfit(cum_n_decks, avg_runtimes_ms, 1))(cum_n_decks),
        color="k",
    )

    plt.title("Avg. runtime vs cumulative number of decks over time.")
    plt.xlabel("Cumulative number of decks")
    plt.ylabel("Avg runtime (ms)")
    lin_fit_eq = "Linear regression:{0}".format(
        np.poly1d(np.polyfit(cum_n_decks, avg_runtimes_ms, 1))
    )
    props = dict(boxstyle="round", facecolor="white", alpha=0.5)
    left, right = plt.xlim()
    _, top = plt.ylim()
    plt.text((right - left) * 0.05, top * 0.9, lin_fit_eq, bbox=props)
    plt.yticks(np.arange(0, max(avg_runtimes_ms), 1))
    plt.show()
