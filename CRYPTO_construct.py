import sqlite3

conn = sqlite3.connect('Database\\test.sqlite')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Record (close REAL, high REAL, low REAL, vol REAL, time INTEGER)')