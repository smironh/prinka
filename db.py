import sqlite3

def check_ref(msg):
    with sqlite3.connect('db.db') as db:
        c = db.cursor()

        info = c.execute('SELECT * FROM ref WHERE user = ?', (msg.chat.id, )).fetchone()
        return info

def add_ref(msg, ref):
    print(ref)
    with sqlite3.connect('db.db') as db:
        c = db.cursor()

        c.execute('INSERT INTO ref(user, ref) VALUES(?, ?)', (msg.chat.id, ref, ))

def profile(msg):
    with sqlite3.connect('db.db') as db:
        c = db.cursor()

        info=c.execute('SELECT count(*) FROM ref WHERE ref = ?', (msg.chat.id, )).fetchone()
        return info