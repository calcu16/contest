#!/home/acarter/local/bin/python3
from os import path
from select import select
from sys import argv, exit, stdin, stdout, stderr

ROOT = "/proj/contest/grader/data"
challenge = open(path.join(ROOT, "%s.in" % argv[1]), "r")
golden = open(path.join(ROOT, "%s.out" % argv[1]), "r")

rlist = [stdin]
wlist = [stdout]

gold = golden.readline()
while gold:
  (input, output, _) = select(rlist,wlist,[],1)
  for file in input:
    if gold != file.readline():
      exit(1)
    gold = golden.readline()
  for file in output:
    line = challenge.readline()
    if not line:
      wlist = []
      try:
        file.close()
      except:
        pass
    else:
      file.write(line)
      file.flush()

try:
  stdout.close()
except:
  pass


