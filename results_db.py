#
# https://docs.python.org/3/library/sqlite3.html
#

import sqlite3

db_name = 'results.sqlite'

def create_DB(self):


    conn = sqlite3.connect(db_name) # create DB file
    cur = conn.cursor()

    # cur.execute('''
    # DROP TABLE IF EXISTS Counts''') # delete table if existing

    cur.execute('''CREATE TABLE Decks (deck_id INTEGER, card TEXT)''')
    cur.execute('''CREATE TABLE Strategies (deck_id INTEGER, card TEXT)''')
    cur.execute('''CREATE TABLE Decks (deck_id INTEGER, card TEXT)''')

    
    cur.close()

def write_result(self, result):

    conn = sqlite3.connect(db_name) # create DB file
    cur = conn.cursor()

    # Iterate over avv results
    # for i in results
    #     cur.execute('''INSERT INTO Counts (email, count)
    #             VALUES (?, 1)''', (email,))
    conn.commit() 
    cur.close()


# import sqlite3
# con = sqlite3.connect('example.db')
# cur = con.cursor()

# # Create table
# cur.execute('''CREATE TABLE stocks
#                (date text, trans text, symbol text, qty real, price real)''')

# # Insert a row of data
# cur.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

# # Save (commit) the changes
# con.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
# con.close()



# Retrieve data
# con = sqlite3.connect('example.db')
# cur = con.cursor()
# for row in cur.execute('SELECT * FROM stocks ORDER BY price'):
#         print(row)
# con.close()