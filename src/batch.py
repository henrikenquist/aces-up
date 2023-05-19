import collections
import functools
import operator
import pprint
import re
import sys
import time

try:
    import winsound  # windows only!
except ModuleNotFoundError:
    pass
from datetime import timedelta

from src import cards, database, game, helpers

RULES = [0, 1, 2, 3, 4, 10, 20, 30, 40, 100, 200, 300, 400, 800, 810, 900, 910, 1000]
EXIT_CODES = ["c", "e", "q", "cancel", "exit", "quit"]


def run(**settings):
    """Test one or more strategies using the same settings and number of decks."""

    # ________________________________________________________________________
    #
    #  Setup
    # ________________________________________________________________________
    my_db = database.Database(settings["DB_NAME"])  # created if not existing
    my_db.save_all = settings["SAVE_ALL"]

    # Settings
    if settings["USE_SUB_SETS"] or settings["PERMUTE"]:
        my_db.trust_random = False
    else:
        my_db.trust_random = settings["TRUST_RANDOM"]
    settings["GAME_PRINT_OUT"] = False
    settings["STRATEGY_PRINT_OUT"] = False

    # Select decks
    n_decks, deck_list, settings["DECKS_FROM_DB"] = _select_decks(my_db)
    if n_decks is None:
        return

    # Edit settings
    response = input("Edit settings (y/n): ").strip().lower()
    if response in EXIT_CODES:
        return
    if response == "y":
        edited_settings = _edit_settings()
        if edited_settings is None:
            return
        settings["USE_SUB_SETS"] = edited_settings[0]
        settings["PERMUTE"] = edited_settings[1]
        my_db.save_all = edited_settings[2]
        my_db.trust_random = edited_settings[3]

    # _________________________________________________________________________
    #
    #  Test one or more strategies using the same settings and number of decks.
    # _________________________________________________________________________
    first_strategy = True
    while True:
        # ________________________________________________________________________
        #
        #  Batch settings
        # ________________________________________________________________________

        if not first_strategy:
            response = input("Test another strategy with same settings (y/n): ")
            if response in EXIT_CODES or response == "n":
                print("\n")
                return
        first_strategy = False  # don't worry, it will run the first one
        game_count = 0  # Game counter
        has_saved_new_batch = False  # Batch flag
        # Batch statistics
        highscore = 0
        n_solutions = 0
        best_deck = 0
        best_strategy = []
        total_rules = []
        score_counts = {}  # {score: counts}
        solutions_per_deck = {}  # {deck nr: counts}

        # Select strategy
        rule_list = _select_strategy()
        if rule_list is None:
            return

        # Number of games, estimated runtime
        n_games, runtime_sec, runtime_str = helpers.get_batch_estimates(
            my_db, n_decks, rule_list, settings["PERMUTE"], settings["USE_SUB_SETS"]
        )

        # Print settings
        _print_settings(my_db, n_games, runtime_str, runtime_sec, rule_list, **settings)

        # Confirm batch run
        response = input("Run batch ('return')?  ").strip().lower()
        if response in EXIT_CODES:
            return

        # ________________________________________________________________________
        #
        #  Batch run
        # ________________________________________________________________________

        # Timer start
        tic = time.perf_counter()
        start_time = time.localtime()
        print("\n===========================================================")
        print(f'Start time:         {time.strftime("%H:%M:%S", start_time)}')
        for deck_nr in deck_list:
            strategies = helpers.get_strategies(
                rule_list, settings["USE_SUB_SETS"], settings["PERMUTE"]
            )

            if settings["DECKS_FROM_DB"]:
                deck = my_db.get_deck(deck_nr)
                if not deck:
                    continue
            else:
                deck = cards.get_new_deck()

            for curr_strategy in strategies:
                game_count += 1

                # Play one game
                curr_game = game.Game(deck, curr_strategy, settings["GAME_PRINT_OUT"])
                curr_game.play()

                if settings["STRATEGY_PRINT_OUT"]:
                    print(
                        "\n==========================================================="
                    )
                    print(
                        f"Deck: {deck_nr}  Game: {game_count}  Strategy: {curr_strategy}"
                    )

                # Batch stats
                # TODO: save score_counts in my_db?
                # TODO: total_rules: use collections.Counter instead?
                score_counts[curr_game.score] = score_counts.get(curr_game.score, 0) + 1
                total_rules.append(curr_game.rule_counts)

                # Alt. 1: save solution for unique: deck + move sequence + strategy
                if my_db.save_all:
                    save_game = curr_game.has_won()
                # Alt. 2: save solution for unique: deck + move sequence
                else:
                    save_game = curr_game.has_won() and my_db.is_unique_solution(
                        deck, curr_game.get_moves()
                    )

                if save_game:
                    solutions_per_deck[deck_nr] = solutions_per_deck.get(deck_nr, 0) + 1

                    if not has_saved_new_batch:
                        new_batch_id = my_db.update_batches(
                            n_decks,
                            str(rule_list),
                            settings["PERMUTE"],
                            settings["USE_SUB_SETS"],
                            n_games,
                            runtime_sec,
                        )
                        has_saved_new_batch = True

                    rule_counts_str = str(
                        sorted(
                            curr_game.rule_counts.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )
                    )
                    my_db.save_solution(
                        deck,
                        curr_game.get_moves(),
                        rule_counts_str,
                        curr_strategy,
                        new_batch_id,
                    )

                    if settings["GAME_PRINT_OUT"]:
                        print(
                            "-----------------------------------------------------------"
                        )
                        print(f"Won game nr:    {game_count}")
                        print(f"Deck nr:        {deck_nr}")
                        print(f"Strategy:       {curr_strategy}")
                        print(f"Runtime:        {time.time() - start_time:0.2f} s")
                        pprint.pprint(
                            sorted(
                                curr_game.rule_counts.items(),
                                key=lambda x: x[1],
                                reverse=True,
                            )
                        )
                        print(
                            "-----------------------------------------------------------\n"
                        )
                        print("Resuming...\n")

                # Highscore
                if curr_game.score > highscore:
                    highscore = curr_game.score
                    best_strategy = curr_strategy
                    best_deck = deck_nr

        # Timer stop
        toc = time.perf_counter()
        elapsed_time_str = "{:0>8}".format(str(timedelta(seconds=round(toc - tic))))
        print(f'Stop time:          {time.strftime("%H:%M:%S", time.localtime())}')

        if has_saved_new_batch:
            my_db.update_runtime(new_batch_id, (toc - tic))

        if game_count == 0:
            print(f"No games run for deck ids {deck_list}.")
            sys.exit()

        print(
            f"Runtime:            {elapsed_time_str}  ({round(toc - tic)} s / {1000*(toc - tic)/game_count:0.2f} ms)"
        )

        try:
            winsound.Beep(2000, 200)
        except ModuleNotFoundError:
            pass

        # ________________________________________________________________________
        #
        #  Batch statistics
        # ________________________________________________________________________

        if has_saved_new_batch:
            _, _, n_solutions, _ = my_db.get_batch_info(new_batch_id)

        # Results
        print("\n===========================================================")
        print(f"Games:              {game_count}")
        print(f"Decks:              {n_decks}")
        print(f"Solved decks:       {len(solutions_per_deck)}")
        print(f"Solutions:          {n_solutions}")
        if has_saved_new_batch:
            print(
                f"Proportion:         {100*n_solutions/n_decks:0.2f} % ({n_solutions/n_decks:0.6f})"
            )
            print(f"Odds:               {n_decks/n_solutions:0.1f}")

        # Solutions per deck
        if has_saved_new_batch and (settings["USE_SUB_SETS"] or settings["PERMUTE"]):
            print("\n===========================================================")
            print(
                f"Solutions per deck (# in batch) for {len(solutions_per_deck)} of {n_decks} decks."
            )
            print("\n")

        # NOTE uncomment if the list is too long
        # if 25 > n_solutions > 0:
            pprint.pprint(
                sorted(solutions_per_deck.items(), key=lambda x: x[1], reverse=True)
            )

        # Scores
        print("\n===========================================================")
        if not has_saved_new_batch:
            print(f"Highest score:     {highscore}")
            print(f"Strategy:          {best_strategy}")
            print(f"Deck nr:           {best_deck}")
        print(f"Score distribution for {game_count} games:")
        if settings["PERMUTE"]:
            print("(Note: Includes potential duplicates since PERMUTE = True)")
            print("\n")
        pprint.pprint(score_counts)

        # Rules
        print("\n===========================================================")
        if has_saved_new_batch:
            rule_counts = my_db.get_rule_counts(batch_id=new_batch_id)
            print(
                f"Rule counts for {n_solutions} solutions ({sum(dict(rule_counts).values())} moves)"
            )
            print("\n")
            pprint.pprint(rule_counts)
            print("\n===========================================================")
        total_rule_stats = dict(
            functools.reduce(operator.add, map(collections.Counter, total_rules))
        )
        print(
            f"Rule counts for {game_count} games ({sum(total_rule_stats.values())} moves)"
        )
        print("\n")
        pprint.pprint(
            sorted(total_rule_stats.items(), key=lambda x: x[1], reverse=True)
        )

        print("\n===========================================================\n\n")
    # ________________________________________________________________________
    #
    #  End batch while loop
    # ________________________________________________________________________


# ________________________________________________________________________
#
#  Helpers
# ________________________________________________________________________


def _edit_settings():
    edited_settings = []
    prompts = [
        "Use sub sets (y/n): ",
        "Use permutations (y/n): ",
        "Save all (y/n): ",
        "Trust random (y/n): ",
    ]
    for prompt in prompts:
        while True:
            response = input(f"{prompt}").strip().lower()
            if response in EXIT_CODES:
                return None
            if response == "y":
                edited_settings.append(True)
                break
            elif response == "n":
                edited_settings.append(False)
                break
            else:
                print("Invalid response. Try again!")

    return edited_settings


def _print_settings(my_db, n_games, runtime_str, runtime_sec, rule_list, **settings):
    print("\n\n===========================================================")
    if (n_games > 1000) and (
        settings["STRATEGY_PRINT_OUT"] or settings["GAME_PRINT_OUT"]
    ):
        print("WARNING: printouts will increase estimated runtime")
    print(f"Rule list:          {rule_list}")
    print(f"Use sub sets:       {settings['USE_SUB_SETS']}")
    print(f"Permute:            {settings['PERMUTE']}")
    print(f"Save all:           {my_db.save_all}")
    print(f"Trust random:       {my_db.trust_random}")
    print(f"Number of games:    {n_games}")
    print(
        f"Estimated runtime:  {runtime_str} ({round(runtime_sec)} s / {1000*runtime_sec/n_games:0.2f} ms)"
    )
    print("\n")


def _select_decks(my_db):
    try:
        n_decks = 0
        response = (
            input("Use new decks ('return') or decks from DB (input deck_ids):  ")
            .strip()
            .lower()
        )
        if response in EXIT_CODES:
            return None, None, None
        elif response:
            decks_from_db = True
            deck_list = list(map(int, re.findall(r"[\d]+", response)))
            n_decks = len(deck_list)
            if not all([d for d in deck_list if my_db.get_deck(d)]):
                raise ValueError("Deck not in database.")
        elif not response:
            decks_from_db = False
            n_decks = int(input("Number of decks: "))
            if n_decks and n_decks > 0:
                deck_list = range(1, n_decks + 1)  # start counting games at 1
    except ValueError as err_msg:
        print(err_msg)
        return None, None, None

    return n_decks, deck_list, decks_from_db


def _select_strategy():  # Select strategy
    print(f"Valid rules: {RULES}\n")
    while True:
        response = input("Select strategy/rule list: ").strip().lower()
        if not response or response in EXIT_CODES:
            return None
        try:
            rule_list = list(map(int, re.findall(r"[\d]+", response)))
            if any(rule not in RULES for rule in rule_list):
                raise ValueError("Invalid strategy format. Please try again!")
            break
        except ValueError as err_msg:
            print(err_msg)

    return rule_list
