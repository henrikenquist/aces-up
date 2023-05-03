import sqlite3
from itertools import accumulate as acc
from collections import defaultdict
import numpy as np
from src import cards


class NotFoundError(Exception):
    pass


class Database:
    """Sqlite database.

    Tables:
    - decks
    - moves
    - strategies
    - batches
    - solutions
    """

    def __init__(self, name: str):
        self.name = name
        self.SAVE_ALL = True
        self.TRUST_RANDOM = True
        self._repr_cache = None
        self._str_cache = None

        conn = sqlite3.connect(name)  # is created if not existing
        cur = conn.cursor()

        cur.execute(
            """CREATE TABLE IF NOT EXISTS decks (
                                            deck_id         INTEGER UNIQUE NOT NULL PRIMARY KEY, 
                                            cards           TEXT
                                            )"""
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS moves (
                                            moves_id        INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                            moves_str       TEXT,
                                            rule_counts     TEXT
                                            )"""
        )
        # one move: (card, from_pile, to_pile, move_count)
        # moves_str: a sequence of moves
        # pile indices: 0-3
        # -1 as from_pile denotes a deal
        # 4 as to_pile denotes a discard

        cur.execute(
            """CREATE TABLE IF NOT EXISTS strategies (
                                            strategy_id     INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                            rule_list       TEXT
                                            )"""
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS batches (
                                                batch_id    INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                                n_decks     INTEGER,
                                                rule_list   TEXT,
                                                permute     INTEGER,
                                                sub_sets    INTEGER,
                                                n_games     INTEGER,
                                                runtime     REAL
                                                )"""
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS solutions (
                                            solution_id     INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                            deck_id         INTEGER,
                                            moves_id        INTEGER,
                                            strategy_id     INTEGER,
                                            batch_id        INTEGER
                                            )"""
        )

        conn.commit()
        cur.close()
        conn.close()

    # _______________________________________________________
    #
    #  Read
    # _______________________________________________________

    def get_db_info(self, *args: str) -> dict:
        """Get database info.
        Return dictionary with input args as keys.

        Options (one or more; as string):
        - 'all'
        - 'n_batches'
        - 'batch_ids'
        - 'n_decks'
        - 'cum_n_decks'
        - 'avg_runtimes'
        """

        try:  # mainly used as a learning example
            conn = sqlite3.connect(self.name)
            cur = conn.cursor()
            db_info = {"self": self.name}
            for item in args:
                if item in ("n_batches", "all"):
                    cur.execute("""SELECT COUNT(*) FROM batches """)
                    n_batches = cur.fetchone()
                    db_info["n_batches"] = n_batches[0]
                if item in ("batch_ids", "all"):
                    batch_ids = []
                    cur.execute(
                        """SELECT batch_id FROM batches ORDER BY batch_id ASC """
                    )
                    batch_rows = cur.fetchall()
                    for batch in batch_rows:
                        batch_ids.append(batch[0])
                    db_info["batch_ids"] = batch_ids
                if item in ("n_decks", "all"):
                    cur.execute(
                        """SELECT batch_id FROM batches ORDER BY batch_id ASC"""
                    )
                    batch_rows = cur.fetchall()
                    n_decks = []
                    for batch_id in batch_rows:
                        n, _, _, _ = self.get_batch_info(batch_id[0])
                        n_decks.append(n)
                    db_info["n_decks"] = n_decks
                if item in ("cum_n_decks", "all"):
                    temp = self.get_db_info("n_decks")
                    db_info["cum_n_decks"] = list(acc(temp["n_decks"]))
                if item in ("avg_runtimes", "all"):
                    cur.execute(
                        """SELECT batch_id FROM batches ORDER BY batch_id ASC"""
                    )
                    batch_rows = cur.fetchall()
                    avg_runtimes = []
                    for batch_id in batch_rows:
                        _, n_games, _, runtime = self.get_batch_info(batch_id[0])
                        avg_runtimes.append(runtime / n_games)
                    db_info["avg_runtimes"] = avg_runtimes
            return db_info
        except sqlite3.OperationalError as err_msg:
            # print(err_msg)
            raise NotFoundError(f"Unable to open database {self.name}") from err_msg

    def get_batch_info(self, batch_id: int) -> list:
        """Return n_decks, n_games, n_solutions, runtime"""
        try:
            # TODO: use *args as in get_db_info() ?
            conn = sqlite3.connect(self.name)
            cur = conn.cursor()
            cur.execute("""SELECT n_decks FROM batches WHERE batch_id=?""", (batch_id,))
            n_decks = cur.fetchone()[0]
            cur.execute("""SELECT n_games FROM batches WHERE batch_id=?""", (batch_id,))
            n_games = cur.fetchone()[0]
            cur.execute("""SELECT runtime FROM batches WHERE batch_id=?""", (batch_id,))
            runtime = cur.fetchone()[0]
            cur.execute(
                """SELECT COUNT(solution_id) FROM solutions WHERE batch_id=?""",
                (batch_id,),
            )
            n_solutions = cur.fetchone()[0]
            return n_decks, n_games, n_solutions, runtime
        except sqlite3.OperationalError as err_msg:
            print(err_msg)
            raise NotFoundError(f"Unable to find batch id {batch_id}") from err_msg
        finally:
            cur.close()
            conn.close()

    def get_avg_runtime(self, new_decks: int = 0) -> float:
        """Calculate predicted average runtime.
        Specify number of decks for new batch. Default = 0.

        Assumed to increase linearly with cumulative number of decks in db.
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        avg_runtime = 0.001  # default to 1 ms if empty database
        lin_reg_limit = 10  # minimum n batches to use linear regression
        runtimes = []
        cum_n_decks = []
        running_val = 0
        db_info = self.get_db_info("batch_ids")
        batch_ids = db_info["batch_ids"]
        # Simple average for small number of batches
        if 0 < len(batch_ids) < lin_reg_limit:
            cur.execute("""SELECT n_games FROM batches""")
            n_games = [sum(x) for x in zip(*cur.fetchall())][0]
            cur.execute("""SELECT runtime FROM batches""")
            tot_time = [sum(x) for x in zip(*cur.fetchall())][0]
            avg_runtime = tot_time / n_games
        # Linear regression for larger total number of decks in batches
        elif len(batch_ids) >= lin_reg_limit:
            for batch_id in batch_ids:
                n_decks, n_games, _, runtime = self.get_batch_info(batch_id)
                running_val += n_decks
                runtimes.append(runtime / n_games)
                cum_n_decks.append(
                    running_val
                )  # TODO: could use itertools.accumulate instead

            slope, intercept = np.polyfit(cum_n_decks, runtimes, 1)

            avg_runtime = intercept + (running_val + new_decks) * slope
        cur.close()
        conn.close()
        return avg_runtime

    def get_rule_counts(self, **kwargs) -> int:
        """Number of times each rule has been used in solutions.
        Return list of tuples sorted by total counts.

        Options (use one or none):
        - solutions_id = [integer]
        - deck_id = [integer]
        - moves_id = [integer]
        - strategy_id = [integer]
        - batch_id    = [integer]
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        temp_list = []
        rule_counts = defaultdict(int)
        if not kwargs:  # get all moves in db
            cur.execute("""SELECT rule_counts FROM moves """)
        else:
            for (
                option,
                id,
            ) in kwargs.items():  # needs to do this way although only one kwargs
                option = "solutions." + option
                query = """SELECT moves.rule_counts
                            FROM moves
                            INNER JOIN solutions
                            ON moves.moves_id = solutions.moves_id
                            WHERE {id_col}=?""".format(
                    id_col=option
                )
                cur.execute(query, (id,))

        moves = cur.fetchall()
        for _, move in enumerate(moves):
            temp_list.extend(eval(move[0]))
        # for row in range(len(moves)):
        #     temp_list.extend(eval(moves[row][0]))
        for rule, count in temp_list:
            rule_counts[rule] += count
        rule_counts = [
            (k, v)
            for (k, v) in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        cur.close()
        conn.close()
        return rule_counts

    def get_strategy_stats(self, curr_strategy: list[int]) -> list[int]:
        """Get stats for given strategy.

        Return n_solutions, n_decks, odds
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        n_solutions = 0
        n_decks = 0
        odds = 0
        if not isinstance(curr_strategy, int):
            rule_list = ",".join(
                [str(e) for _, e in enumerate(curr_strategy)]
            )  # eg: '1,20,100'

        else:
            cur.execute(
                """SELECT rule_list FROM strategies WHERE strategy_id=?""",
                (curr_strategy,),
            )
            rule_list = cur.fetchone()[0]
        cur.execute(
            """SELECT strategy_id FROM strategies WHERE rule_list=?""",
            (rule_list,),
        )
        strategy_id = cur.fetchone()[0]
        if strategy_id:
            cur.execute(
                """SELECT COUNT(*) FROM solutions WHERE strategy_id=?""",
                (strategy_id,),
            )
            n_solutions = cur.fetchone()[0]
            cur.execute(
                """SELECT DISTINCT batch_id FROM solutions WHERE strategy_id=?""",
                (strategy_id,),
            )  # get unique batches
            batch_rows = cur.fetchall()
            for batch in batch_rows:
                cur.execute(
                    """SELECT n_decks FROM batches WHERE batch_id=?""",
                    (batch[0],),
                )
                n_decks += cur.fetchone()[0]
        cur.close()
        conn.close()
        odds = n_decks / n_solutions
        return n_solutions, n_decks, odds

    def get_strategy_stats_list(
        self, sort_by: str = "odds", min_n_decks: int = 100_000
    ) -> list[dict]:
        """Get strategy stats list.

        Options:
        - Sort by 'solutions', 'decks', or 'odds'. Default 'odds'
        - Minimum number of decks for strategy. Default 100 000

        Return sorted list of dictionaries:
        {'Strategy': [], 'Solutions': [], 'Decks': [], 'Odds': []}
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        stats_list = []
        asc = True
        cur.execute("""SELECT * FROM strategies """)
        strategy_rows = cur.fetchall()
        for strat in strategy_rows:
            n_solutions, n_decks, odds = self.get_strategy_stats(strat[0])
            stats_list.append(
                {
                    "Strategy": strat[1],
                    "Solutions": n_solutions,
                    "Decks": n_decks,
                    "Odds": odds,
                }
            )
        stats_list = [e for e in stats_list if e["Decks"] >= min_n_decks]
        if str.capitalize(sort_by) == "Odds":
            asc = False
        stats_list = sorted(
            stats_list, key=lambda x: x[str.capitalize(sort_by)], reverse=asc
        )
        cur.close()
        conn.close()
        return stats_list

    def get_deck(self, deck_id: int) -> list[cards.Card]:
        """Get deck from DB."""

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        deck = []
        cur.execute("""SELECT cards FROM decks WHERE deck_id=?""", (deck_id,))
        card_str = cur.fetchone()
        if card_str:
            deck = cards.get_deck_from_str(card_str[0])
        # else:
        #     print(f'Deck ID {deck_id} not in database {self.name}')
        cur.close()
        conn.close()
        return deck

    # _______________________________________________________
    #
    #  Validate
    # _______________________________________________________

    def is_new_deck(self, curr_deck):
        """Check if deck is in database. Return is_new, deck_id, cards.

        A deck is defined by a unique string of cards.
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        curr_cards = ",".join(
            [str(e) for _, e in enumerate(curr_deck)]
        )  # eg: '4h,Td,9c,...'
        cur.execute(
            "SELECT * FROM decks WHERE cards=? ", (curr_cards,)
        )  # VALUES must be a tuple or a list
        deck_row = cur.fetchone()
        if deck_row is None:
            is_new = True
            cur.execute("SELECT COUNT(deck_id) FROM decks")
            deck_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            deck_id = deck_row[0]
        conn.commit()
        cur.close()
        conn.close()
        return is_new, deck_id, curr_cards

    def is_new_move_sequence(self, curr_moves):
        """Check is move sequence is in database.

        A move is defined by a list: [card, from_pile, to_pile, rule_str, move_count].
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        # one move: [card, from_pile, to_pile, move_count]
        moves_str = ",".join([str(e) for _, e in enumerate(curr_moves)])

        cur.execute("SELECT * FROM moves WHERE moves_str=? ", (moves_str,))
        move_row = cur.fetchone()
        if move_row is None:
            is_new = True
            cur.execute("SELECT COUNT(moves_id) FROM moves")
            moves_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            moves_id = move_row[0]
        conn.commit()
        cur.close()
        conn.close()
        return is_new, moves_id, moves_str

    def is_new_strategy(self, curr_strategy: list[int]) -> bool:
        """Check if strategy is in database. Return is_new, strategy_id, rule_list.

        A strategy is defined by a unique string of rules.
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        rule_list = ",".join(
            [str(e) for _, e in enumerate(curr_strategy)]
        )  # eg: '1,20,100'
        cur.execute("SELECT * FROM strategies WHERE rule_list=? ", (rule_list,))
        strategy_row = cur.fetchone()
        if strategy_row is None:
            is_new = True
            cur.execute("SELECT COUNT(strategy_id) FROM strategies")
            strategy_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            strategy_id = strategy_row[0]
        conn.commit()
        cur.close()
        conn.close()
        return is_new, strategy_id, rule_list

    def is_new_solution(self, deck_id: int, moves_id: int, strategy_id: int) -> bool:
        """Check if solution is in database.

        def: A solution is defined by a combination of deck and move sequence.
        setting: self.SAVE_ALL == True -> save all solutions (default)
        setting: self.SAVE_ALL == False -> save unique solutions only
        return: is_new
        rtype is_new: bool
        return: solution_id
        rtype solutions_id: int
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        if self.SAVE_ALL:
            cur.execute(
                """SELECT * FROM solutions WHERE deck_id=? AND moves_id=? AND strategy_id=?""",
                [deck_id, moves_id, strategy_id],
            )
            solution_row = cur.fetchone()
        else:
            cur.execute(
                """SELECT * FROM solutions WHERE deck_id=? AND moves_id=?""",
                [deck_id, moves_id],
            )
            solution_row = cur.fetchone()
        if solution_row is None:
            is_new = True
            cur.execute("""SELECT COUNT(solution_id) FROM solutions""")
            solution_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            solution_id = solution_row[0]
        conn.commit()
        cur.close()
        conn.close()
        return is_new, solution_id

    def is_new_batch(self, batch_id: int) -> bool:
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("""SELECT * FROM batches WHERE batch_id=?""", (batch_id,))
        batch_row = cur.fetchone()

        if batch_row is None:
            is_new = True
            cur.execute("SELECT COUNT(*) FROM solutions")
            batch_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            batch_id = batch_row[0]
        conn.commit()
        cur.close()
        conn.close()
        return is_new, batch_id

    def is_unique_solution(self, curr_deck: list[cards.Card], curr_moves: list) -> bool:
        """Check if a combination of deck and moves is a unique solution (regardless of strategy)."""

        is_new_d, _, _ = self.is_new_deck(curr_deck)
        is_new_m, _, _ = self.is_new_move_sequence(curr_moves)

        if (is_new_d and is_new_m) or (not is_new_d and is_new_m):
            return True
        else:
            return False

    # _______________________________________________________
    #
    #  Update
    # _______________________________________________________

    def save_solution(
        self,
        deck: list[cards.Card],
        moves: list,
        rule_counts: dict,
        strategy: list[int],
        batch_id: int,
    ) -> None:
        """Save data for new solution to database."""

        # Deck
        deck_id = self._update_decks(deck)

        # Moves
        moves_id = self._update_moves(moves, rule_counts)

        # Strategy
        strategy_id = self._update_strategies(strategy)

        # Solutions
        solution_id = self._update_solutions(deck_id, moves_id, strategy_id, batch_id)

    def _update_decks(self, curr_deck: list[cards.Card]) -> int:
        """Add deck if not in database or if TRUST_RANDOM == True

        Return deck_id.
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        # the faster way, trusting randomness (52!)
        if self.TRUST_RANDOM:
            is_new = True
            curr_cards = ",".join([str(c) for _, c in enumerate(curr_deck)])
            cur.execute("SELECT COUNT(deck_id) FROM decks")
            deck_id = cur.fetchone()[0] + 1
        # deck randomness: the slower but bullet-proof way:
        else:
            is_new, deck_id, curr_cards = self.is_new_deck(curr_deck)

        if is_new:
            # print(f'Saving new deck. Number of decks in db: {deck_id}')
            cur.execute(
                """INSERT INTO decks (deck_id, cards) VALUES (?,?)""",
                (deck_id, curr_cards),
            )
        conn.commit()
        cur.close()
        conn.close()
        return deck_id

    def _update_moves(self, curr_moves: list, rule_counts: dict) -> int:
        """Add move sequence for solution.

        A move is defined by a list: [card, from_pile, to_pile, rule_str, move_count].
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        is_new, moves_id, moves_str = self.is_new_move_sequence(curr_moves)
        # one move: [card, from_pile, to_pile, move_count]
        if is_new:
            # print(f'Saving new move sequence.')
            cur.execute(
                """INSERT INTO moves (moves_id, moves_str, rule_counts) VALUES (?,?,?)""",
                (moves_id, moves_str, rule_counts),
            )
        conn.commit()
        cur.close()
        conn.close()
        return moves_id

    def _update_strategies(self, curr_strategy: list[int]) -> int:
        """Add strategy if not in database. Return strategy_id.

        A strategy is defined by a unique list of rules.
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        is_new, strategy_id, rule_list = self.is_new_strategy(curr_strategy)
        if is_new:
            # print(f'Saving new strategy. Number of strategies in db: {strategy_id}')
            cur.execute(
                """INSERT INTO strategies (strategy_id, rule_list) VALUES (?,?)""",
                (strategy_id, rule_list),
            )
        conn.commit()
        cur.close()
        conn.close()
        return strategy_id

    def _update_solutions(
        self, deck_id: int, moves_id: int, strategy_id: int, batch_id: int
    ) -> int:
        """Add solution if not in database. Return solution_id.

        A solution is defined by unique combination of deck and moves.
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        is_new, solution_id = self.is_new_solution(deck_id, moves_id, strategy_id)
        if is_new:
            # print(f'Saving new solution.')
            cur.execute(
                """INSERT INTO solutions (solution_id, deck_id, moves_id, strategy_id, batch_id) VALUES (?,?,?,?,?)""",
                (solution_id, deck_id, moves_id, strategy_id, batch_id),
            )
        conn.commit()
        cur.close()
        conn.close()
        return solution_id

    def update_batches(
        self,
        n_decks: int,
        rule_list: list[int],
        permute: bool,
        sub_sets: bool,
        n_games: int,
        runtime: float,
    ) -> int:
        """Add batch if not in database. Return batch_id.

        A batch is a set of games defined by a number of decks and a set of strategies.
        """

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM batches")
        batch_id = cur.fetchone()[0] + 1
        cur.execute(
            """INSERT INTO batches (batch_id, n_decks, rule_list, permute, sub_sets, n_games, runtime) VALUES (?,?,?,?,?,?,?)""",
            (batch_id, n_decks, rule_list, permute, sub_sets, n_games, runtime),
        )
        conn.commit()
        cur.close()
        conn.close()
        return batch_id

    def update_runtime(self, batch_id: int, runtime: float) -> None:
        """Update runtime for batch."""

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute(
            """UPDATE batches SET runtime=? WHERE batch_id=?""",
            (runtime, batch_id),
        )

        conn.commit()
        cur.close()
        conn.close()

    # _______________________________________________________
    #
    #  Database
    # _______________________________________________________

    def delete_tables(self, *args) -> None:
        """Delete table in DB."""

        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        for table_name in args:
            cur.execute(" DROP TABLE ? IF EXISTS ", (table_name,))
        conn.commit()
        cur.close()
        conn.close()
