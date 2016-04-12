to set up database and run these files:

install vagrant virtual machine

navigate to directory with vagrantfile

run vagrant up

run vagrant ssh

cd ../../vagrant/tournament/

run psql

create database schema with:
\i tournament

open another vagrant ssh connection

cd ../../vagrant/tournament/

run python tournament_test.py

do all 10 tests pass?  if so, great.  if not, fix tournament.py