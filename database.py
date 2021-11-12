import sqlite3
from collections import defaultdict
import numpy as np

class Database:
    """ Sqlite database.

        Tables:
        - decks
        - moves
        - strategies
        - batches
        - solutions
    """

    def __init__(self, db_name):
       
        self.db_name     = db_name
        self._repr_cache = None
        self._str_cache  = None

        conn = sqlite3.connect(db_name) # is created if not existing
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS decks (
                                            deck_id         INTEGER UNIQUE NOT NULL PRIMARY KEY, 
                                            cards           TEXT
                                            )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS moves (
                                            moves_id        INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                            moves_str       TEXT,
                                            rule_counts     TEXT
                                            )''')
                                            # one move: (card, from_pile, to_pile, move_count)
                                            # moves_str: a sequence of moves
        
        cur.execute('''CREATE TABLE IF NOT EXISTS strategies (
                                            strategy_id     INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                            rule_list       TEXT
                                            )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS batches (
                                                batch_id    INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                                n_decks     INTEGER,
                                                rule_list   TEXT,
                                                permute     INTEGER,
                                                sub_sets    INTEGER,
                                                n_games     INTEGER,
                                                runtime     REAL
                                                )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS solutions (
                                            solution_id     INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                            deck_id         INTEGER,
                                            moves_id        INTEGER,
                                            strategy_id     INTEGER,
                                            batch_id        INTEGER
                                            )''')

        conn.commit() 
        cur.close()

    # _______________________________________________________________________________________________________
    #
    #  Read
    # _______________________________________________________________________________________________________

    def get_db_info(self, *args):
        """ Get database info.
            Return dictionary with input args as keys.

            Options (one or more; as string):
            - 'all'
            - 'n_batches'
            - 'batch_ids'
            - 'avg_runtimes'
            - 'cum_n_decks'
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        db_info = {'self': self.db_name}

        # TODO expand with further functionality
        for item in args:

            if item == 'n_batches' or item == 'all':
                cur.execute('''SELECT COUNT(*) FROM batches ''')
                n_batches = cur.fetchone()
                db_info['n_batches'] = n_batches[0]

            if item == 'batch_ids' or item == 'all':
                batch_ids = []
                cur.execute('''SELECT batch_id FROM batches ORDER BY batch_id ASC ''')
                batch_rows = cur.fetchall()

                for batch in batch_rows:
                    batch_ids.append(batch[0])

                db_info['batch_ids'] = batch_ids

            if item == 'avg_runtimes' or item == 'all':
                cur.execute('''SELECT batch_id FROM batches ORDER BY batch_id ASC''')
                batch_rows = cur.fetchall()
                
                avg_runtimes = []

                for batch_id in batch_rows:
                    _, n_games, _, runtime = self.get_batch_info(batch_id[0])
                    avg_runtimes.append(runtime/n_games)

                db_info['avg_runtimes'] = avg_runtimes
            
            
            if item == 'cum_n_decks' or item == 'all':
                cur.execute('''SELECT batch_id FROM batches ORDER BY batch_id ASC''')
                batch_rows = cur.fetchall()
                
                cum_n_decks = []
                running_val = 0

                for batch_id in batch_rows:
                    n_decks, _, _, _ = self.get_batch_info(batch_id[0])
                    running_val += n_decks
                    cum_n_decks.append(running_val)

                db_info['cum_n_decks'] = cum_n_decks

        cur.close()

        return db_info

    def get_batch_info(self, batch_id):
        """ Return n_decks, n_games, n_solutions, runtime
        """

        # TODO: use *args as in get_db_info() ?
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute('''SELECT n_decks FROM batches WHERE batch_id=?''', (batch_id,))
        n_decks = cur.fetchone()[0]
        cur.execute('''SELECT n_games FROM batches WHERE batch_id=?''', (batch_id,))
        n_games = cur.fetchone()[0]
        cur.execute('''SELECT runtime FROM batches WHERE batch_id=?''', (batch_id,))
        runtime = cur.fetchone()[0]
        cur.execute('''SELECT COUNT(solution_id) FROM solutions WHERE batch_id=?''', (batch_id,))
        n_solutions = cur.fetchone()[0]

        cur.close()

        return n_decks, n_games, n_solutions, runtime

    def get_avg_runtime(self, new_decks=0):
        """ Calculate predicted average runtime.
            Specify number of decks for new batch. Default = 0.

            Assumed to increase linearly with cumulative number of decks in db.
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        avg_runtime     = 0.001 # default to 1 ms if empty database
        lin_reg_limit   = 10    # minimum n batches to use linear regression 
        runtimes        = []
        cum_n_decks     = []
        running_val     = 0
        db_info         = self.get_db_info('batch_ids')
        batch_ids       = db_info['batch_ids']

        # Simple average for small number of batches:
        if 0 < len(batch_ids) < lin_reg_limit:
            cur.execute('''SELECT n_games FROM batches''')
            n_games = [sum(x) for x in zip(*cur.fetchall())][0] # [0] since value returned as list
            cur.execute('''SELECT runtime FROM batches''')
            tot_time = [sum(x) for x in zip(*cur.fetchall())][0]
            avg_runtime = tot_time/n_games

        # Linear regression for larger number of batches (or rather, decks):
        elif len(batch_ids) >= lin_reg_limit:
            # print('lin. regr. used for runtime average')
            for batch_id in batch_ids:
                n_decks, n_games, _, runtime = self.get_batch_info(batch_id)
                running_val += n_decks
                runtimes.append(runtime/n_games)
                cum_n_decks.append(running_val)

            # TODO: Should weigh runtime according to number of games in batch
            # Now each batch is treated equally, regardless of 1 game or 1,000,000 games
            slope, intercept = np.polyfit(cum_n_decks, runtimes, 1)

            avg_runtime = intercept + (running_val + new_decks) * slope

        cur.close()

        return avg_runtime

    def get_rule_counts(self, **kwargs):
        """ Number of times each rule has been used in solutions.
            Return list of tuples sorted by total counts.

            Options (use one or none):
            - solutions_id = [integer]
            - deck_id = [integer]
            - moves_id = [integer]
            - strategy_id = [integer]
            - batch_id    = [integer]
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        temp_list = []
        rule_counts = defaultdict(int)

        if not kwargs: # get all moves in db
            cur.execute('''SELECT rule_counts FROM moves ''')
        else:
            for option, id in kwargs.items(): # needs to do this way although only one kwargs
                option = 'solutions.' + option
                query = '''SELECT moves.rule_counts
                            FROM moves
                            INNER JOIN solutions
                            ON moves.moves_id = solutions.moves_id
                            WHERE {id_col}=?'''.format(id_col=option)
                cur.execute(query, (id,))

        moves = cur.fetchall()

        for row in range(len(moves)):
            temp_list.extend(eval(moves[row][0]))

        for rule, count in temp_list:
            rule_counts[rule] += count
        
        rule_counts = [(k, v) for (k, v) in sorted(rule_counts.items(), key=lambda x:x[1], reverse=True)]

        cur.close()

        return rule_counts

    def get_strategy_stats(self, curr_strategy):
        """ Get stats for given strategy.

            Return n_solutions, n_decks, odds
        """
        
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        n_solutions = 0
        n_decks     = 0
        odds        = 0

        if not type(curr_strategy) == int:
            rule_list   = ",".join([str(e) for _,e in enumerate(curr_strategy)]) # eg: '1,20,100'
        
        else:
            cur.execute('''SELECT rule_list FROM strategies WHERE strategy_id=?''', (curr_strategy, ))
            rule_list = cur.fetchone()[0]

        cur.execute('''SELECT strategy_id FROM strategies WHERE rule_list=?''', (rule_list, ))
        strategy_id = cur.fetchone()[0]

        if strategy_id:
            cur.execute('''SELECT COUNT(*) FROM solutions WHERE strategy_id=?''', (strategy_id, ))
            n_solutions = cur.fetchone()[0]

            cur.execute('''SELECT DISTINCT batch_id FROM solutions WHERE strategy_id=?''', (strategy_id, )) # get unique batches
            batch_rows = cur.fetchall()

            for batch in batch_rows:
                cur.execute('''SELECT n_decks FROM batches WHERE batch_id=?''', (batch[0], ))
                n_decks += cur.fetchone()[0]

        cur.close()
        odds = n_decks/n_solutions

        return n_solutions, n_decks, odds

    def get_strategy_stats_list(self, sort_by='odds', min_n_decks=100000):
        """ Get strategy stats list.
            
            Options:
            - Sort by 'solutions', 'decks', or 'odds'. Default 'odds'
            - Minimum number of decks for strategy. Default 100 000

            Return sorted list of dictionaries:
            {'Strategy': [], 'Solutions': [], 'Decks': [], 'Odds': []}
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        
        stats_list = []
        asc = True

        cur.execute('''SELECT * FROM strategies ''')
        strategy_rows = cur.fetchall()

        for strat in strategy_rows:
            n_solutions, n_decks, odds = self.get_strategy_stats(strat[0])
            stats_list.append({'Strategy': strat[1], 'Solutions': n_solutions, 'Decks': n_decks, 'Odds': odds})
        
        stats_list = [e for e in stats_list if e['Decks'] >= min_n_decks]

        if str.capitalize(sort_by) == 'Odds': asc = False

        stats_list = sorted(stats_list, key=lambda x:x[str.capitalize(sort_by)], reverse=asc)

        cur.close()

        return stats_list

    # _______________________________________________________________________________________________________
    #
    #  Validate
    # _______________________________________________________________________________________________________

    def is_new_deck(self, curr_deck):
        """ Check if deck is in database. Return is_new, deck_id, cards.
        
            A deck is defined by a unique string of cards.
        """
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cards = ",".join([str(e) for _,e in enumerate(curr_deck)]) # eg: '4h,Td,9c,...'

        cur.execute('SELECT * FROM decks WHERE cards=? ', (cards,) ) # VALUES must be a tuple or a list
        deck_row = cur.fetchone()

        if deck_row == None:
            is_new = True
            cur.execute('SELECT COUNT(deck_id) FROM decks')
            deck_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            deck_id = deck_row[0]

        conn.commit() 
        cur.close()

        return is_new, deck_id, cards

    def is_new_move_sequence(self, curr_moves):
        """ Check is move sequence is in database.

            A move is defined by a list: [card, from_pile, to_pile, rule_str, move_count].
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        # one move: [card, from_pile, to_pile, move_count]
        moves_str = ",".join([str(e) for _,e in enumerate(curr_moves)])

        cur.execute('SELECT * FROM moves WHERE moves_str=? ', (moves_str,) )
        move_row = cur.fetchone()

        if move_row == None:
            is_new = True
            cur.execute('SELECT COUNT(moves_id) FROM moves')
            moves_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            moves_id = move_row[0]

        conn.commit()
        cur.close()

        return is_new, moves_id, moves_str
    
    def is_new_strategy(self, curr_strategy):
        """ Check if strategy is in database. Return is_new, strategy_id, rule_list.

            A strategy is defined by a unique string of rules.
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        rule_list = ",".join([str(e) for _,e in enumerate(curr_strategy)]) # eg: '1,20,100'

        cur.execute('SELECT * FROM strategies WHERE rule_list=? ', (rule_list,) )
        strategy_row = cur.fetchone()

        if strategy_row == None:
            is_new = True
            cur.execute('SELECT COUNT(strategy_id) FROM strategies')
            strategy_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            strategy_id = strategy_row[0]

        conn.commit() 
        cur.close()

        return is_new, strategy_id, rule_list

    def is_new_solution(self, deck_id, moves_id):
        """ Check if solution is in database. Return is_new, solution_id.

            A solution is defined by unique combination of deck and moves.
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute('''SELECT * FROM solutions WHERE deck_id=? AND moves_id=?''', [deck_id, moves_id] )
        solution_row = cur.fetchone()

        if solution_row == None:
            is_new = True
            cur.execute('''SELECT COUNT(solution_id) FROM solutions''')
            solution_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            solution_id = solution_row[0]
            
        conn.commit() 
        cur.close()

        return is_new, solution_id

    def is_new_batch(self, batch_id):

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute('''SELECT * FROM batches WHERE batch_id=?''', (batch_id, ) )
        batch_row = cur.fetchone()

        if batch_row == None:
            is_new = True
            cur.execute('SELECT COUNT(*) FROM solutions')
            batch_id = cur.fetchone()[0] + 1
        else:
            is_new = False
            batch_id = batch_row[0]

        conn.commit() 
        cur.close()

        return is_new, batch_id

    def is_unique_solution(self, curr_deck, curr_moves):
        """ Check if a combination of deck and moves is a unique solution (regardless of strategy).
        """

        is_new_d, _, _ = self.is_new_deck(curr_deck)
        is_new_m, _, _ = self.is_new_move_sequence(curr_moves)

        if (is_new_d and is_new_m) or (not is_new_d and is_new_m):
            return True
        else:
            return False

    # _______________________________________________________________________________________________________
    #
    #  Update
    # _______________________________________________________________________________________________________

    def save_solution(self, deck, moves, rule_counts, strategy, batch_id):
        """ Save data for new unique solution to database.
        """

        # Deck
        deck_id     = self.update_decks(deck)

        # Moves
        moves_id    = self.update_moves(moves, rule_counts)

        # Strategy
        strategy_id = self.update_strategies(strategy)
        
        # Solutions
        solution_id = self.update_solutions(deck_id, moves_id, strategy_id, batch_id)

    def update_decks(self, curr_deck):
        """ Add deck if not in database. Return deck_id.

            A deck is defined by a unique string of cards.
        """
        
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        is_new, deck_id, cards = self.is_new_deck(curr_deck)

        if is_new:
            # print(f'Saving new deck. Number of decks in db: {deck_id}')
            cur.execute('''INSERT INTO decks (deck_id, cards) VALUES (?,?)''',
                                            (deck_id, cards))

        conn.commit() 
        cur.close()

        return deck_id

    def update_moves(self, curr_moves, rule_counts):
        """ Add move sequence for solution.

            A move is defined by a list: [card, from_pile, to_pile, rule_str, move_count].
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        is_new, moves_id, moves_str = self.is_new_move_sequence(curr_moves)

        # one move: [card, from_pile, to_pile, move_count]
        if is_new:
            # print(f'Saving new move sequence.')
            cur.execute('''INSERT INTO moves (moves_id, moves_str, rule_counts) VALUES (?,?,?)''',
                                            (moves_id, moves_str, rule_counts))

        conn.commit() 
        cur.close()

        return moves_id

    def update_strategies(self, curr_strategy):
        """ Add strategy if not in database. Return strategy_id.

            A strategy is defined by a unique string of rules.
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        is_new, strategy_id, rule_list = self.is_new_strategy(curr_strategy)

        if is_new:
            # print(f'Saving new strategy. Number of strategies in db: {strategy_id}')
            cur.execute('''INSERT INTO strategies (strategy_id, rule_list) VALUES (?,?)''',
                                                (strategy_id, rule_list))

        conn.commit() 
        cur.close()

        return strategy_id

    def update_solutions(self, deck_id, moves_id, strategy_id, batch_id):
        """ Add solution if not in database. Return solution_id.

            A solution is defined by unique combination of deck and moves.
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        is_new, solution_id = self.is_new_solution(deck_id, moves_id)

        if is_new:
            # print(f'Saving new solution.')
            cur.execute('''INSERT INTO solutions (solution_id, deck_id, moves_id, strategy_id, batch_id) VALUES (?,?,?,?,?)''',
                                                (solution_id, deck_id, moves_id, strategy_id, batch_id))
            
        conn.commit() 
        cur.close()

        return solution_id

    def update_batches(self, n_decks, rule_list, permute, sub_sets, n_games, runtime):
        """ Add batch if not in database. Return batch_id.

            A batch is a set of games defined by a number of decks and a set of strategies.
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        cur.execute('SELECT COUNT(*) FROM batches')
        batch_id = cur.fetchone()[0] + 1

        cur.execute('''INSERT INTO batches (batch_id, n_decks, rule_list, permute, sub_sets, n_games, runtime) VALUES (?,?,?,?,?,?,?)''',
                                        (batch_id, n_decks, rule_list, permute, sub_sets, n_games, runtime))

        conn.commit() 
        cur.close()

        return batch_id

    def update_runtime(self, batch_id, runtime):
        """ Update runtime for batch.
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute('''UPDATE batches SET runtime=? WHERE batch_id=?''', (runtime, batch_id))

        conn.commit() 
        cur.close()

    # _______________________________________________________________________________________________________
    #
    #  Database                       
    # _______________________________________________________________________________________________________

    def delete_tables(self, *args):
        """ Delete table in DB.
        """

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()

        for table_name in args:
            cur.execute(' DROP TABLE ? IF EXISTS ', (table_name,))
        
        conn.commit() 
        cur.close()

