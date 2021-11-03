import sqlite3
from collections import defaultdict
# https://docs.python.org/3/library/sqlite3.html


# _______________________________________________________________________________________________________
#
#  Validation methods                          
# _______________________________________________________________________________________________________

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

# https://stackoverflow.com/questions/39793327/sqlite3-insert-if-not-exist-with-python

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
# 
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

# https://stackoverflow.com/questions/39793327/sqlite3-insert-if-not-exist-with-python

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


def update_batches(db_name, n_decks, rule_list, permute, sub_sets, games, runtime):
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

    cur.execute('''INSERT INTO batches (batch_id, n_decks, rule_list, permute, sub_sets, games, runtime) VALUES (?,?,?,?,?,?,?)''',
                                       (batch_id, n_decks, rule_list, permute, sub_sets, games, runtime))

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
#  Reading methods
# _______________________________________________________________________________________________________

def get_avg_runtime(db_name):
    """ Calculate average runtime from batches.
    """
    avg_runtime = 0.001 # default to 1 ms

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute('''SELECT games FROM batches''')

    n_games = [sum(x) for x in zip(*cur.fetchall())]
    cur.execute('''SELECT runtime FROM batches''')
    tot_time = [sum(x) for x in zip(*cur.fetchall())]

    avg_runtime = tot_time[0]/n_games[0]

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
        for item in kwargs.items():
            if item.key == 'batch_id': # select via combo of solution table and moves table
                cur.execute('''SELECT rule_counts FROM moves WHERE batch_id=?''', (item.value, ))

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
                                        cards           STRING
                                        )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS moves (
                                        moves_id        INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                        moves_str       STRING,
                                        rule_counts     STRING
                                        )''')
                                        # one move: (card, from_pile, to_pile, move_count)
                                        # moves_str: a sequence of moves
    
    cur.execute('''CREATE TABLE IF NOT EXISTS strategies (
                                        strategy_id     INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                        rule_list       STRING
                                        )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS batches (
                                            batch_id    INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                            n_decks     INTEGER,
                                            rule_list   STRING,
                                            permute     BOOLEAN,
                                            sub_sets    BOOLEAN,
                                            games       INTEGER,
                                            runtime     INTEGER
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

