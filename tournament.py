#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import pprint
pp = pprint.pprint



def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cur  = conn.cursor()

    cur.execute("delete from matches;")
    cur.execute("update players set wins = 0")
    cur.execute("update playersomw set (matches, wins, omw) = (0, 0, 0)") # extra credit


    conn.commit()
    cur.close()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    
    conn = connect()
    cur  = conn.cursor()

    cur.execute("delete from players")
    conn.commit()

    cur.close()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cur  = conn.cursor()

    cur.execute("select count(name) from players;")
    result = cur.fetchone()[0]

    cur.close()
    conn.close()

    return result


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cur  = conn.cursor()

    initial_wins = 0
    cur.execute("insert into players (name, wins) "
        "values(%s, %s)",
        (name, initial_wins))
    conn.commit()

    cur.close()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cur  = conn.cursor()

    ### simple standings ### replaced by extra-credit standings below
    # cur.execute('''
    #     select 
    #         players.id, 
    #         name, 
    #         wins, 
    #         cast(count(matches.id) as int) as matches
    #     from 
    #         players left outer join matches
    #     on 
    #         players.id = matches.winner or
    #         players.id = matches.loser 
    #     group by 
    #         players.id 
    #     order by 
    #         wins desc
    #     ''')
    # standings = cur.fetchall()

    # extra credit:
    """When two players have the same number of wins, rank them according to OMW (Opponent Match Wins), the total number of wins by players they have played against.
    """
    # add column owm to players
    # cur.execute('''
    #     alter table players
    #     add omw int
    #     ''')
    # conn.commit()

    #for player i:
    cur.execute("select * from players")
    for player in cur.fetchall():
        playerid = player[0]
        #list opponents
        opponents = []
        # list winning opponents of lost matches
        cur.execute("select loser from matches where winner = %s",(playerid,))
        for result in cur.fetchall():
            if result[0] not in opponents:
                opponents.append(result[0])
        # list losing opponents of won matches  
        cur.execute("select winner from matches where loser = %s",(playerid,))
        for result in cur.fetchall():
            if result[0] not in opponents:
                opponents.append(result[0])
        # build opponent wins
        opponentwins = 0
        for opponent in opponents:
            cur.execute("select wins from players where id = %s",(opponent,))
            opponentwins += cur.fetchone()[0]
            cur.execute("update players set omw = %s where id = %s",(opponentwins, playerid))
            conn.commit()

    cur.execute('''
        select 
            players.id, 
            name, 
            wins, 
            cast(count(matches.id) as int) as matches
        from 
            players left outer join matches
        on 
            players.id = matches.winner or
            players.id = matches.loser 
        group by 
            players.id 
        order by 
            wins desc,
            omw  desc
        ''')
    standings = cur.fetchall()
    psqlprint("players")
    pp(standings)

    conn.commit()
    cur.close()
    conn.close()

    return standings



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    # update matches
    conn = connect()
    cur  = conn.cursor()
    cur.execute("insert into matches (winner, loser) values (%s, %s)",
        (winner, loser))
    conn.commit()

    cur.close()
    conn.close()

    # update winning player
    conn = connect()
    cur  = conn.cursor()

    cur.execute("select wins from players where id = %s", (winner,))
    wins = cur.fetchone()[0]
    wins += 1
    cur.execute("update players set wins = %s where id = %s", (wins, winner))
    conn.commit()

    cur.close()
    conn.close()

#################################### my addition #############################

def psqlprint(my_table_call):
    ''' useing if statements because I can't access (psycopg2 intentionally prohibits accessing) tables parametrically.

        loosely based on this:
        http://stackoverflow.com/questions/10252247/how-do-i-get-a-list-of-column-names-from-a-psycopg2-cursor
    '''
    # must import pprint
    pp = pprint.pprint
    conn = connect()
    cur = conn.cursor()
    if my_table_call in ["matches", "all"]:
        my_table_name = "matches"
        cur.execute("select column_name from information_schema.columns where table_name=%s",(my_table_name,))
        column_names = [row[0] for row in cur]
        cur.execute("select * from matches order by id")
        rows = [row + (" \n ",) for row in cur.fetchall()] # \n ensures prettiness
        lines = "=" * ((sum(len(col) for col in column_names)) + len(column_names)*4)
       
        print
        pp([" "*(len(lines)/3)
                 + my_table_name 
                 + " "*(len(lines)*2/3 - len(my_table_name)),
            lines,
            column_names,
            lines,
            rows])
        print

    if my_table_call in ["players", "all"]:
        my_table_name = "players"
        cur.execute("select column_name from information_schema.columns where table_name=%s",(my_table_name,))
        column_names = [row[0] for row in cur]
        cur.execute("select * from players  order by id")
        lines = "=" * ((sum(len(col) for col in column_names)) + len(column_names)*4)
       
        print
        pp([" "*(len(lines)/3)
                 + my_table_name 
                 + " "*(len(lines)*2/3 - len(my_table_name)),
            lines,
            column_names, 
            lines,
            cur.fetchall()])
        print

    if my_table_call in ["playersomw", "all"]:
        my_table_name = "playersomw"
        cur.execute("select column_name from information_schema.columns where table_name=%s",(my_table_name,))
        column_names = [row[0] for row in cur]
        cur.execute("select * from playersomw  order by id")
        lines = "=" * ((sum(len(col) for col in column_names)) + len(column_names)*4)
       
        print
        pp([" "*(len(lines)/3)
                 + my_table_name 
                 + " "*(len(lines)*2/3 - len(my_table_name)),
            lines,
            column_names, 
            lines,
            cur.fetchall()])
        print

    cur.close()
    conn.close()


###################### end my addition #######################
 
def swissPairings(standings):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    pairings = []
    for i in range(0, len(standings), 2):
        pairings.append((   standings[i]  [0],
                            standings[i]  [1],
                            standings[i+1][0],
                            standings[i+1][1]))
    return pairings


















