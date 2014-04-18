#!/home/acarter/local/bin/python3
from datetime import datetime, timedelta
from os import path
from sqlite3 import connect
from subprocess import Popen, TimeoutExpired
from sys import argv, exit, stdin, stdout, stderr

ROOT = "/proj/contest"
DB = path.join(ROOT, "db/contest.db")
TXT = path.join(ROOT, "grader/txt/")

epoch = datetime.utcfromtimestamp(0)

conn = connect(DB)
test = argv[1]
uid = argv[2]

cur = conn.cursor()

cur.execute("select t_name from tests where t_name = ?", [test])

result = cur.fetchone()

if not result:
  print("No test named '%s'" % test, file=stderr)
  exit(1)

start = datetime.utcnow()
start = (start - epoch) // timedelta(microseconds=1)

cur.execute("insert into checkouts (c_uid, c_test, c_start) values (?, ?, ?)", [uid, test, start])
conn.commit()

for line in open(path.join(TXT, test)):
  stderr.write(line)

