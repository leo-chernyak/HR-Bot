import sqlite3

conn = sqlite3.connect("dataUser.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (chatId INTEGER, autoSend BOOLEAN, status TEXT)")
conn.commit()
conn.close()
