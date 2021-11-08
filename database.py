import sqlite3
from collections import defaultdict
import numpy as np
# https://docs.python.org/3/library/sqlite3.html


# _______________________________________________________________________________________________________
#
#  Reading methods
# _______________________________________________________________________________________________________

def get_db_info(db_name, *args, **kwargs):
    """ Get database info.
        Use input arguments to select type of info:
        - 'n_batches'
        - 'batch_ids'
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    db_info = {'db_name': db_name}

    # TODO expande with further functionality
    for item in args:
        if item == 'n_batches':
            cur.execute('''SELECT COUNT(*) FROM batches ''')
            n_batches = cur.fetchone()
            db_info['n_batches'] = n_batches[0]
        if item == 'batch_ids':
            batch_ids = []
            cur.execute('''SELECT batch_id FROM batches ORDER BY batch_id ASC ''')
            batch_rows = cur.fetchall()
            for batch in batch_rows:
                batch_ids.append(batch[0])
            db_info['batch_ids'] = batch_ids
        if item == 'cum_n_batches':
            batch_ids = []
            cur.execute('''SELECT batch_id FROM batches ORDER BY batch_id ASC''')
            batch_rows = cur.fetchall()
            for batch in batch_rows:
                batch_ids.append(batch[0])
            db_info['batch_ids'] = batch_ids

    cur.close()

    return db_info

def get_batch_info(db_name, batch_id):
    """ Return n_decks, n_games, runtime
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('''SELECT n_decks FROM batches WHERE batch_id=?''', (batch_id,))
    n_decks = cur.fetchone()[0]
    cur.execute('''SELECT n_games FROM batches WHERE batch_id=?''', (batch_id,))
    n_games = cur.fetchone()[0]
    cur.execute('''SELECT runtime FROM batches WHERE batch_id=?''', (batch_id,))
    runtime = cur.fetchone()[0]

    cur.close()

    return n_decks, n_games, runtime

def get_avg_runtime(db_name, new_decks=0):
    """ Calculate predicted average runtime.
        Specify number of decks for new batch. Default = 0.

        Assumed to increase linearly with cumulative number of decks in db.
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    avg_runtime = 0.001 # default to 1 ms

    runtimes    = []
    cum_n_decks = []
    running_val = 0
    db_info     = get_db_info(db_name, 'batch_ids')
    batch_ids   = db_info['batch_ids']

    for batch_id in batch_ids:
        n_decks, n_games, runtime = get_batch_info(db_name, batch_id)
        running_val += n_decks
        runtimes.append(runtime/n_games)
        cum_n_decks.append(running_val)

    slope, intercept = np.polyfit(cum_n_decks, runtimes, 1)

    avg_runtime = intercept + (running_val + new_decks) * slope

    # Simple average:
    # cur.execute('''SELECT games FROM batches''')
    # n_games = [sum(x) for x in zip(*cur.fetchall())][0] # [0] since value returned as list
    # cur.execute('''SELECT runtime FROM batches''')
    # tot_time = [sum(x) for x in zip(*cur.fetchall())][0]
    # avg_runtime = tot_time/n_games

    cur.close()

    return avg_runtime

def get_rule_counts(db_name, **kwargs):
    """ Total number of times each rule has been used in solutions.
        Return list sorted by count values.
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    complete_list = []
    rule_counts = defaultdict(int)
    
    # TODO: selection options via kwargs
    if kwargs:
        pass
        # for item in kwargs.items():
            # rule counts per strategy
            # select all solutions for strategy
            # select all moves for these solutions
            # if item.key == 'strategy_id': # select via combo of solution table and moves table
            #     cur.execute('''SELECT rule_counts FROM moves INNER JOIN solutions ON solutions.moves_id = moves.moves_id''', (strategy_id, ))
            #     pass

    else:
        cur.execute('''SELECT rule_counts FROM moves ''')

    moves = cur.fetchall()

    for row in range(len(moves)):
        complete_list.extend(eval(moves[row][0]))

    for k, v in complete_list:
        rule_counts[k] += v
    
    rule_counts = [(k, v) for (k, v) in sorted(rule_counts.items(), key=lambda x:x[1], reverse=True)]

    cur.close()

    return rule_counts

def get_strategy_stats(db_name, curr_strategy):
    """ Get stats for given strategy.

        Return n_solutions, n_decks, odds
    """
    
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    n_solutions = 0
    n_decks     = 0
    odds        = 0

    if not type(curr_strategy) == int:
        rule_list   = ",".join([str(e) for _,e in enumerate(curr_strategy)]) # eg: '1,20,100'
    
    else: # curr_strategy used as strategy_id in method call
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

def get_strategy_stats_list(db_name, sort_by='odds', min_n_decks=100000):
    """ Get strategy stats list.
        
        Options:
        - Sort by 'solutions', 'decks', or 'odds'. Default 'odds'
        - Minimum number of decks for strategy. Default 100 000

        Return sorted list of dictionaries:
        {'Strategy': [], 'Solutions': [], 'Decks': [], 'Odds': []}
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    stats_list = []
    asc = True

    cur.execute('''SELECT * FROM strategies ''')
    strategy_rows = cur.fetchall()

    for strat in strategy_rows:
        n_solutions, n_decks, odds = get_strategy_stats(db_name, strat[0])
        stats_list.append({'Strategy': strat[1], 'Solutions': n_solutions, 'Decks': n_decks, 'Odds': odds})
    
    stats_list = [e for e in stats_list if e['Decks'] >= min_n_decks]

    if str.capitalize(sort_by) == 'Odds': asc = False

    stats_list = sorted(stats_list, key=lambda x:x[str.capitalize(sort_by)], reverse=asc)

    cur.close()

    return stats_list


# _______________________________________________________________________________________________________
#
#  Validation methods                          
# _______________________________________________________________________________________________________
#
# https://stackoverflow.com/questions/39793327/sqlite3-insert-if-not-exist-with-python 

def is_new_deck(db_name, curr_deck):
    """ Check if deck is in database. Return is_new, deck_id, cards.
    
        A deck is defined by a unique string of cards.
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cards = ",".join([str(e) for _,e in enumerate(curr_deck)]) # eg: '4h,Td,9c,...'
    # print('Cards in deck', cards)

    cur.execute('SELECT * FROM decks WHERE cards=? ', (cards,) ) # VALUES must be a tuple or a list
    deck_row = cur.fetchone()

    if deck_row == None:
        is_new = True
        cur.execute('SELECT COUNT(*) FROM decks')
        deck_id = cur.fetchone()[0] + 1
    else:
        is_new = False
        deck_id = deck_row[0]

    conn.commit() 
    cur.close()

    return is_new, deck_id, cards

def is_new_move_sequence(db_name, curr_moves):
    """ Check is move sequence is in database.

        A move is defined by a list: [card, from_pile, to_pile, rule_str, move_count].
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # one move: [card, from_pile, to_pile, move_count]
    moves_str = ",".join([str(e) for _,e in enumerate(curr_moves)])

    cur.execute('SELECT * FROM moves WHERE moves_str=? ', (moves_str,) )
    move_row = cur.fetchone()

    if move_row == None:
        is_new = True
        cur.execute('SELECT COUNT(*) FROM moves')
        moves_id = cur.fetchone()[0] + 1
    else:
        is_new = False
        moves_id = move_row[0]

    conn.commit()
    cur.close()

    return is_new, moves_id, moves_str
   
def is_new_strategy(db_name, curr_strategy):
    """ Check if strategy is in database. Return is_new, strategy_id, rule_list.

        A strategy is defined by a unique string of rules.
    """



    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    rule_list = ",".join([str(e) for _,e in enumerate(curr_strategy)]) # eg: '1,20,100'

    cur.execute('SELECT * FROM strategies WHERE rule_list=? ', (rule_list,) )
    strategy_row = cur.fetchone()

    if strategy_row == None:
        is_new = True
        cur.execute('SELECT COUNT(*) FROM strategies')
        strategy_id = cur.fetchone()[0] + 1
    else:
        is_new = False
        strategy_id = strategy_row[0]

    conn.commit() 
    cur.close()

    return is_new, strategy_id, rule_list

def is_new_solution(db_name, deck_id, moves_id):
    """ Check if solution is in database. Return is_new, solution_id.

        A solution is defined by unique combination of deck and moves.
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('''SELECT * FROM solutions WHERE deck_id=? AND moves_id=?''', [deck_id, moves_id] )
    solution_row = cur.fetchone()

    if solution_row == None:
        is_new = True
        cur.execute('SELECT COUNT(*) FROM solutions')
        solution_id = cur.fetchone()[0] + 1
    else:
        is_new = False
        solution_id = solution_row[0]
        
    conn.commit() 
    cur.close()

    return is_new, solution_id

def is_new_batch(db_name, batch_id):

    conn = sqlite3.connect(db_name)
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

def is_unique_solution(db_name, curr_deck, curr_moves):
    """ Check if a combination of deck and moves is a unique solution (regardless of strategy).
    """

    is_new_d, _, _ = is_new_deck(db_name, curr_deck)
    is_new_m, _, _ = is_new_move_sequence(db_name, curr_moves)

    if (is_new_d and is_new_m) or (not is_new_d and is_new_m):
        return True
    else:
        return False


# _______________________________________________________________________________________________________
#
#  Update methods                                
# _______________________________________________________________________________________________________
#
# https://stackoverflow.com/questions/39793327/sqlite3-insert-if-not-exist-with-python

def save_solution(db_name, deck, moves, rule_counts, strategy, batch_id):
    """ Save data for new unique solution to database.
    """

    # Deck
    deck_id     = update_decks(db_name, deck)

    # Moves
    moves_id    = update_moves(db_name, moves, rule_counts)

    # Strategy
    strategy_id = update_strategies(db_name, strategy)
    
    # Solutions
    solution_id = update_solutions(db_name, deck_id, moves_id, strategy_id, batch_id)

def update_decks(db_name, curr_deck):
    """ Add deck if not in database. Return deck_id.

        A deck is defined by a unique string of cards.
    """
    
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    is_new, deck_id, cards = is_new_deck(db_name, curr_deck)

    if is_new:
        # print(f'Saving new deck. Number of decks in db: {deck_id}')
        cur.execute('''INSERT INTO decks (deck_id, cards) VALUES (?,?)''',
                                         (deck_id, cards))

    conn.commit() 
    cur.close()

    return deck_id

def update_moves(db_name, curr_moves, rule_counts):
    """ Add move sequence for solution.
        A move is defined by a list: [card, from_pile, to_pile, rule_str, move_count].
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    is_new, moves_id, moves_str = is_new_move_sequence(db_name, curr_moves)

    # one move: [card, from_pile, to_pile, move_count]
    if is_new:
        # print(f'Saving new move sequence.')
        cur.execute('''INSERT INTO moves (moves_id, moves_str, rule_counts) VALUES (?,?,?)''',
                                         (moves_id, moves_str, rule_counts))

    conn.commit() 
    cur.close()

    return moves_id

def update_strategies(db_name, curr_strategy):
    """ Add strategy if not in database. Return strategy_id.

        A strategy is defined by a unique string of rules.
    """



    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    is_new, strategy_id, rule_list = is_new_strategy(db_name, curr_strategy)

    if is_new:
        # print(f'Saving new strategy. Number of strategies in db: {strategy_id}')
        cur.execute('''INSERT INTO strategies (strategy_id, rule_list) VALUES (?,?)''',
                                              (strategy_id, rule_list))

    conn.commit() 
    cur.close()

    return strategy_id

def update_solutions(db_name, deck_id, moves_id, strategy_id, batch_id):
    """ Add solution if not in database. Return solution_id.

        A solution is defined by unique combination of deck and moves.
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    is_new, solution_id = is_new_solution(db_name, deck_id, moves_id)

    if is_new:
        # print(f'Saving new solution.')
        cur.execute('''INSERT INTO solutions (solution_id, deck_id, moves_id, strategy_id, batch_id) VALUES (?,?,?,?,?)''',
                                             (solution_id, deck_id, moves_id, strategy_id, batch_id))
        
    conn.commit() 
    cur.close()

    return solution_id

def update_batches(db_name, n_decks, rule_list, permute, sub_sets, n_games, runtime):
    """ Add batch if not in database. Return batch_id.

        A batch is a set of games defined by number of decks in .
        Useful for calculating odds (tot nr batches / tot nr solutions)
        for a particular strategy or in general.
        See table solutions.
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM batches')
    batch_id = cur.fetchone()[0] + 1

    cur.execute('''INSERT INTO batches (batch_id, n_decks, rule_list, permute, sub_sets, n_games, runtime) VALUES (?,?,?,?,?,?,?)''',
                                       (batch_id, n_decks, rule_list, permute, sub_sets, n_games, runtime))

    conn.commit() 
    cur.close()

    return batch_id

def update_runtime(db_name, batch_id, runtime):
    """ Update runtime for batch.
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute('''UPDATE batches SET runtime=? WHERE batch_id=?''', (runtime, batch_id))

    conn.commit() 
    cur.close()


# _______________________________________________________________________________________________________
#
#  Database                       
# _______________________________________________________________________________________________________

def create_db(db_name):
    """ Create solutions database
    """

    conn = sqlite3.connect(db_name) # creates if not existing
    cur = conn.cursor()

    # cur.execute(''' DROP TABLE IF EXISTS decks ''') # delete table if existing

    # https://python-forum.io/thread-33533.html

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

def delete_tables(db_name, *args):

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    for table_name in args:
        cur.execute(' DROP TABLE IF EXISTS VALUES (?) ', table_name)
    
    conn.commit() 
    cur.close()

