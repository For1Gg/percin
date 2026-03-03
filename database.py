import sqlite3 as sq

class Database(object):
    def __init__(self, path):
        self.connection = sq.connect(path)
        self.connection.execute('pragma foreign_keys = on')
        self.connection.commit()
        self.cur = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.query(
            'CREATE TABLE IF NOT EXISTS triggers ('
            'ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            'trigger TEXT)')
        
        self.query(
            'CREATE TABLE IF NOT EXISTS monitored_chats ('
            'ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            'chat_id INTEGER, '
            'chat_title TEXT, '
            'chat_username TEXT, '
            'chat_type TEXT)')
        
        self.query(
            'CREATE TABLE IF NOT EXISTS found_messages ('
            'ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            'message_id INTEGER, '
            'chat_id INTEGER, '
            'sender_id INTEGER, '
            'sender_name TEXT, '
            'sender_username TEXT, '
            'message_text TEXT, '
            'found_triggers TEXT, '
            'date TEXT)')

    def query(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        self.connection.commit()

    def fetchone(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchone()

    def fetchall(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchall()

    def __del__(self):
        self.connection.close()