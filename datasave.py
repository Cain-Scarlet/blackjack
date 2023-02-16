import os
import sqlite3

DB_PATH = os.path.expanduser('C:/Users/Cain Scarlet/Desktop/black_jack.db')

con = None
cur = None

if not os.path.exists(DB_PATH):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("CREATE TABLE 'UserInfo' ('Qid' integer NOT NULL,'Coin' integer NOT NULL,PRIMARY KEY ('Qid'));")
    con.commit()
else:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()


def player_exist(qq) -> bool:
    sql = f'select count(1) from UserInfo where Qid={qq}'
    return cur.execute(sql).fetchone()[0] == 1


def player_init(qq):
    sql = f'insert into UserInfo values({qq},256)'
    cur.execute(sql)
    con.commit()


def get_coin(qq) -> int:
    sql = f'select Coin from UserInfo where Qid={qq}'
    return int(cur.execute(sql).fetchone()[0])


def batch_save(bets: list):
    for qq in bets:
        if bets[qq] >= 0:
            sql = f'update UserInfo set Coin=Coin+{bets[qq]} where Qid={qq}'
        else:
            sql = f'update UserInfo set Coin=Coin-{-bets[qq]} where Qid={qq}'
        cur.execute(sql)
        con.commit()


def add_coin(qq, count):
    if not player_exist(qq):
        player_init(qq)
    sql = f'update UserInfo set Coin=Coin+{count} where Qid={qq}'
    cur.execute(sql)
    con.commit()
