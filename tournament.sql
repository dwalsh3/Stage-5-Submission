-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- database should be named "tournament"

-- to execute these commands, either:
-- 1)  paste into psql
-- 2)  run \i tournament.sql from commandline (\i for import, executes the sql commands within the sql file from psql)


-- to drop hard-to-drop databases (to avoid error: "cannot drop the currently open database"):
	-- select * from pg_stat_activity where datname = 'tournament';
	-- select pg_terminate_backend (pg_stat_activity.pid) from pg_stat_activity where pg_stat_activity.datname = 'tournament';
	-- OR
	-- exit psql, then sudo service postgresql restart

--According to the POSTGRESQL docs at Postgres Manual, there is no meta command which will only close the current connection (without closing the PSQL application using \q). The only way to close the current connection is to connect to another database using \connect, as described in the docs mentioned above:
drop database if exists test;
create database test;

drop database if exists tournament;
create database tournament;
\c tournament;

create table Players (
	id      serial primary key,
	name    text,
	wins    int,
	omw		int
	);

create table Matches (
	id      serial primary key,
	winner  int references Players(id),
	loser   int references Players(id),
	);

-- create view (dan)