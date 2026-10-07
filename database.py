import sqlite3


def get_connection():
    conn = sqlite3.connect("carmatch.db")
    conn.row_factory= sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
