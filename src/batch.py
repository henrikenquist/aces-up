from src import game, cards, database, helpers

import re, time, pprint, winsound
import collections, functools, operator
from sys import exit
from datetime import timedelta

# from tqdm import tqdm


def run(settings):
    # ________________________________________________________________________
    #
    #  Batch settings
    # ________________________________________________________________________

    db_name = settings[0]
    USE_SUB_SETS = settings[1]
    PERMUTE = settings[2]
    STRATEGY_PRINT_OUT = settings[3]
    GAME_PRINT_OUT = settings[4]
    # TODO
    # RECURSIVE       = settings[5]

    # ________________________________________________________________________
    #
    #  Batch variables
    # ________________________________________________________________________

    # Database
    db = database.Database(db_name)  # is created if not existing
    # Game counter
    game_count = 0
    # Batch flag
    has_saved_new_batch = False
    # Batch statistics
    highscore = 0
    n_solutions = 0
    best_strategy = []
    total_rules = []
    score_counts = {}  # {score: counts}
    solutions_per_deck = {}  # {deck nr: counts}

    # ________________________________________________________________________
    #
    #  User input (at runtime)
    # ________________________________________________________________________

    # Strategy
    response = input("Rule list: ")
    if response:
        rule_list = list(map(int, re.findall(r"[\d]+", response)))
    else:
        exit()

    # Decks
    response = input("Use new decks (return) or decks from DB (input ids):  ")
    if response:
        DECKS_FROM_DB = True
        deck_list = list(map(int, re.findall(r"[\d]+", response)))
        n_decks = len(deck_list)
    else:
        DECKS_FROM_DB = False
        n_decks = int(input("Number of decks: "))
        if n_decks and n_decks > 0:
            deck_list = range(1, n_decks + 1)  # start counting games at 1
        else:
            exit()

    # Number of games and estimated runtime
    n_games, runtime_sec, runtime_str = helpers.get_batch_estimates(
        db, n_decks, rule_list, PERMUTE, USE_SUB_SETS
    )

    print("\n\n===========================================================")
    if (n_games > 1000) and (STRATEGY_PRINT_OUT or GAME_PRINT_OUT):
        print("WARNING: printouts will increase estimated runtime")
    print(f"Rule list:          {rule_list}")
    print(f"Use sub sets:       {USE_SUB_SETS}")
    print(f"Permute:            {PERMUTE}")
    print(f"Number of games:    {n_games}")
    print(
        f"Estimated runtime:  {runtime_str} ({round(runtime_sec)} s / {1000*runtime_sec/n_games:0.2f} ms)"
    )
    print("\n")

    response = input("Continue (return) or quit (q)?  ")
    if response == "q":
        exit()

    # Timer start
    tic = time.perf_counter()
    start_time = time.localtime()
    print("\n===========================================================")
    print(f'Start time:         {time.strftime("%H:%M:%S", start_time)}')

    # ________________________________________________________________________
    #
    #  Batch loop
    # ________________________________________________________________________

    # for deck_nr in tqdm(deck_list, desc='Looping decks'):
    for deck_nr in deck_list:

        strategies = helpers.get_strategies(rule_list, USE_SUB_SETS, PERMUTE)

        if DECKS_FROM_DB:
            deck = db.get_deck(deck_nr)
            if not deck:
                continue
        else:
            deck = cards.get_new_deck()

        # for curr_strategy in tqdm(strategies, desc='Looping strategies'):
        for curr_strategy in strategies:

            game_count += 1

            # Play one game
            curr_game = game.Game(deck, curr_strategy, GAME_PRINT_OUT)
            curr_game.play()

            if STRATEGY_PRINT_OUT:
                print(
                    "\n==========================================================="
                )
                print(
                    f"Deck: {deck_nr}  Game: {game_count}  Strategy: {curr_strategy}"
                )

            # Batch stats
            # TODO: save score_counts in DB?
            # TODO: total_rules: use collections.Counter instead
            score_counts[curr_game.score] = (
                score_counts.get(curr_game.score, 0) + 1
            )
            total_rules.append(curr_game.rule_counts)

            # Save in DB if is unique solution
            if curr_game.has_won() and db.is_unique_solution(
                deck, curr_game.get_moves()
            ):

                solutions_per_deck[deck_nr] = (
                    solutions_per_deck.get(deck_nr, 0) + 1
                )

                if not has_saved_new_batch:
                    new_batch_id = db.update_batches(
                        n_decks,
                        str(sorted(rule_list)),
                        PERMUTE,
                        USE_SUB_SETS,
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
                db.save_solution(
                    deck,
                    curr_game.get_moves(),
                    rule_counts_str,
                    curr_strategy,
                    new_batch_id,
                )

                if GAME_PRINT_OUT:
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
        db.update_runtime(new_batch_id, (toc - tic))

    if game_count == 0:
        print(f"No games run for deck ids {deck_list}.")
        exit()

    print(
        f"Runtime:            {elapsed_time_str}  ({round(toc - tic)} s / {1000*(toc - tic)/game_count:0.2f} ms)"
    )

    winsound.Beep(2000, 750)

    # ________________________________________________________________________
    #
    #  Batch statistics
    # ________________________________________________________________________

    if has_saved_new_batch:
        _, _, n_solutions, _ = db.get_batch_info(new_batch_id)

    # Settings
    print("\n===========================================================")
    print(f"Unique solutions:   {n_solutions}")
    print(f"Games:              {game_count}")
    print(f"Decks:              {n_decks}")
    if has_saved_new_batch:
        print(
            f"Proportion:         {100*n_solutions/n_decks:0.2f} % ({n_solutions/n_decks:0.6f})"
        )
        print(f"Odds:               {n_decks/n_solutions:0.1f}")

    # Unique solutions
    if has_saved_new_batch:
        print("\n===========================================================")
        print(
            f"Unique solutions per deck ({len(solutions_per_deck)} of {n_decks} decks)"
        )
        print("\n")

    if 25 > n_solutions > 0:
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
    if PERMUTE:
        print("(NB: includes potential duplicates since PERMUTE = True)")
        print("\n")
    pprint.pprint(score_counts)

    # Rules
    print("\n===========================================================")
    if has_saved_new_batch:
        rule_counts = db.get_rule_counts(batch_id=new_batch_id)
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
