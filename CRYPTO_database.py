import sqlite3

class Save():
    def __init__(self):
        self.conn = sqlite3.connect('Database\\test.sqlite')
        self.cur = self.conn.cursor()

    def save(self, data):
        self.cur.execute('''INSERT INTO Record (close, high, low, vol, time) VALUES (?, ?, ?, ?, ?)''', 
                        ( data[0],data[1],data[2],data[3],data[4] ) )
        self.conn.commit()