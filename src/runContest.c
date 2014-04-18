/*
 * runContest.c
 *
 * To be run with setuid to contest
 *
 */

#include <errno.h>
#include <fcntl.h>
#include <pwd.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include "runContest.h"

#define STDIN  0
#define STDOUT 1
#define STDERR 2

#define CHECK_ERROR(func, error) do { if((func) == -1) { error; } } while(0)
#define CHECK_TRUE(func, error) do { if(func) { error; } } while(0)

char gprog[] = "/proj/contest/grader/bin/grader.py";

int
forkProg(char **argv, int infd, int outfd, int asUser)
{
  int pid, ec = 1;
  pid = fork();
  if (pid == -1) {
    return -1;
  } else if (pid == 0) {
    if(asUser)
      CHECK_ERROR(seteuid(getuid()), goto __error);
    else
      CHECK_ERROR(setreuid(geteuid(),geteuid()), goto __error);

    if(asUser)
      CHECK_ERROR(close(STDERR), goto __error);
    else
      CHECK_ERROR(dup2(STDOUT,STDERR), goto __error);

    CHECK_ERROR(dup2(infd,STDIN), goto __error);
    CHECK_ERROR(dup2(outfd,STDOUT), goto __error);

    if(!asUser)
      CHECK_TRUE(errno = clearenv(), goto __error);
    CHECK_ERROR(execvp(argv[0], argv), goto __error);
  }
  close(infd);
  close(outfd);
  return pid;
__error:
  fprintf(stderr, "Failure to fork %s: %s\n", argv[0], strerror(errno));
  exit(-1);
}

int
main(int argc, char **argv)
{
  char *grader[4], **command = NULL, uid[65];
  int fdPG[2], fdGP[2], ppid = -1, gpid = -1, status;
  if (argc < 3) {
    fprintf(stderr,"%s [PROBLEM] [COMMAND] [ARGS]\n",argv[0]);
    return 1;
  }

  sprintf(uid, "%d", getuid());

  grader[0] = gprog;
  grader[1] = argv[1];
  grader[2] = uid;
  grader[3] = NULL;
  command = argv + 2;

  CHECK_ERROR(pipe(fdGP), goto __error);
  CHECK_ERROR(pipe(fdPG), goto __error);

  CHECK_ERROR(ppid = forkProg(command, fdGP[STDIN], fdPG[STDOUT], 1), goto __error);
  CHECK_ERROR(gpid = forkProg(grader, fdPG[STDIN], fdGP[STDOUT], 0), goto __error);

  /* clean-up */
  waitpid(gpid, &status, 0);
  kill(ppid, 9);
  waitpid(ppid, NULL, 0);

  return status;
__error:
  fprintf(stderr, "Failed to grade: %s\n", strerror(errno));
  if(ppid != -1) {
    kill(ppid, 9);
    waitpid(ppid, NULL, WNOHANG);
  }
  if(gpid != -1) {
    kill(gpid, 9);
    waitpid(gpid, NULL, WNOHANG);
  }
  return 1;
}

