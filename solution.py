import sqlite3
# https://docs.python.org/3/library/sqlite3.html


def save_in_db(db_name, deck, strategy, moves):
    """ Write results to database.
    """

    # Deck
    deck_id     = update_decks(db_name, deck)

    # Strategy
    strategy_id = update_strategies(db_name, strategy)

    # Solutions
    solution_id = update_solutions(db_name, deck_id, strategy_id)

    # Moves
    update_moves(db_name, solution_id, moves)


# _______________________________________________________________________________________________________
#
#  Update methods                                
# _______________________________________________________________________________________________________

def update_decks(db_name, curr_deck):
    """ Add deck if not in database. Return deck_id.

        A deck is defined by a unique string of cards.
    """
    
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cards = ",".join([str(e) for _,e in enumerate(curr_deck)]) # eg: '4h,Td,9c,...'
    # print('Cards in deck', cards)

    cur.execute('SELECT * FROM decks WHERE cards=? ', (cards,) ) # VALUES must be a tuple or a list
    deck_row = cur.fetchone()

    if deck_row == None:
        cur.execute('SELECT COUNT(*) FROM decks')
        deck_id = cur.fetchone()[0] + 1
        print(f'Saving new deck. Number of decks in db: {deck_id}')
        cur.execute('''INSERT INTO decks (deck_id, cards) VALUES (?,?)''',
                                         (deck_id, cards))
    else:
        # print('Deck found in db')
        deck_id = deck_row[0]

    conn.commit() 
    cur.close()

    return deck_id


def update_strategies(db_name, curr_strategy):
    """ Add strategy if not in database. Return strategy_id.

        A strategy is defined by a unique string of rules.
    """

# https://stackoverflow.com/questions/39793327/sqlite3-insert-if-not-exist-with-python

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    rule_list = ",".join([str(e) for _,e in enumerate(curr_strategy)]) # eg: '1,20,100'

    cur.execute('SELECT * FROM strategies WHERE rule_list=? ', (rule_list,) )
    strategy_row = cur.fetchone()

    if strategy_row == None:
        cur.execute('SELECT COUNT(*) FROM strategies')
        strategy_id = cur.fetchone()[0] + 1
        print(f'Saving new strategy. Number of strategies in db: {strategy_id}')
        cur.execute('''INSERT INTO strategies (strategy_id, rule_list) VALUES (?,?)''',
                                              (strategy_id, rule_list))
    else:
        # print('Strategy found in db')
        strategy_id = strategy_row[0]

    conn.commit() 
    cur.close()

    return strategy_id


def update_solutions(db_name, deck_id, strategy_id):
    """ Add solution if not in database. Return solution_id.

        A solution is defined by unique combination of deck and strategy.
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('''SELECT * FROM solutions WHERE deck_id=? AND strategy_id=?''', [deck_id, strategy_id] )
    solution_row = cur.fetchone()

    if solution_row == None:
        cur.execute('SELECT COUNT(*) FROM solutions')
        solution_id = cur.fetchone()[0] + 1

        print(f'Saving new solution.')
        print('\n')
        cur.execute('''INSERT INTO solutions (solution_id, deck_id, strategy_id) VALUES (?,?,?)''',
                                             (solution_id, deck_id, strategy_id))
    else:
        # print('Solution found in db')
        solution_id = solution_row[0]
        
    conn.commit() 
    cur.close()

    return solution_id


def update_moves(db_name, solution_id, moves):
    """ Add moves for solution.
        A move is defined by a list: [card, from_pile, to_pile, rule_str, move_count].
    """

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # one move: [card, from_pile, to_pile, rule_str, move_count]
    move_str = ",".join([str(e) for _,e in enumerate(moves)])
    cur.execute('''INSERT INTO moves (solution_id, move) VALUES (?,?)''',
                                        (solution_id, move_str))

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
                                        deck_id INTEGER UNIQUE NOT NULL PRIMARY KEY, 
                                        cards STRING
                                        )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS strategies (
                                        strategy_id INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                        rule_list STRING
                                        )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS solutions (
                                        solution_id INTEGER UNIQUE NOT NULL PRIMARY KEY,
                                        deck_id INTEGER,
                                        strategy_id INTEGER
                                        )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS moves (
                                        solution_id INTEGER,
                                        move STRING 
                                        )''')
                                        # move: (card, from_pile, to_pile, rule_str, move_count)

    conn.commit() 
    cur.close()


def delete_tables(db_name, *args):

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    for table_name in args:
        cur.execute(' DROP TABLE IF EXISTS VALUES (?) ', table_name)
    
    conn.commit() 
    cur.close()

