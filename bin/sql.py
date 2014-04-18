#!/home/acarter/local/bin/python3
from sqlite3 import connect
from sys import stdin

conn = connect("/proj/contest/db/contest.db")
script = "\n".join(stdin.readlines())
conn.executescript(script)

