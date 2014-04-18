#!/home/acarter/local/bin/python3
from datetime import datetime, timedelta
from os import path
from sqlite3 import connect
from subprocess import Popen, TimeoutExpired
from sys import argv, exit, stdin, stdout, stderr

ROOT = "/proj/contest"
DB = path.join(ROOT, "db/contest.db")
BIN = path.join(ROOT, "grader/bin/")

epoch = datetime.utcfromtimestamp(0)

conn = connect(DB)
test = argv[1]
uid = argv[2]

cur = conn.cursor()

cur.execute("select t_grader, t_timeout from tests where t_name = ?", [test])

result = cur.fetchone()

if not result:
  print("No test named '%s'" % test, file=stderr)
  exit(1)

start = datetime.utcnow()
start = (start - epoch) // timedelta(microseconds=1)

cur.execute("insert into results (r_uid, r_test, r_start) values (?, ?, ?)", [uid, test, str(start)])
conn.commit()

grader, timeout = result


try:
  proc = Popen([path.join(BIN, grader), test])
  stdout.close()
  print("Grading....",file=stderr)
  ec = proc.wait(int(timeout))
  end = datetime.utcnow()
except TimeoutExpired:
  ec = None
  end = datetime.utcnow()
  proc.kill()
  proc.wait()

if ec is None:
  result = "Timed out"
elif ec:
  result = "Failed"
else:
  result = "Passed"

end   = (end - epoch) // timedelta(microseconds=1)

cur.execute("update results SET r_end = ?, r_result = ? WHERE r_uid = ? and r_test = ? and r_start = ?", [str(end), result, uid, test, str(start)])

print("Program %s in %dus" % (result, end - start), file=stderr)

conn.commit()

conn.close()


