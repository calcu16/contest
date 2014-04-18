create table if not exists tests(t_name UNIQUE, t_grader, t_timeout);

insert or replace into tests values('cat', 'simple.py', '10');

