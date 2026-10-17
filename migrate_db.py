"""Copy the local ta_fitness database to a hosted MySQL (one-off, run on your PC).

Set the remote details as environment variables, then run:  python migrate_db.py
    TA_REMOTE_HOST, TA_REMOTE_PORT, TA_REMOTE_USER, TA_REMOTE_PASSWORD, TA_REMOTE_DB
    optional: TA_REMOTE_CA = path to the provider's ca.pem (required for Aiven)
"""
import os
import certifi
import pymysql
import streamlit as st

TABLES = ["members", "user_login", "attendance", "payments", "quiz_scores", "login_attempts"]

local = dict(st.secrets["mysql"])

src = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **local)
dst = pymysql.connect(
    host=os.environ["TA_REMOTE_HOST"],
    port=int(os.environ.get("TA_REMOTE_PORT", 3306)),
    user=os.environ["TA_REMOTE_USER"],
    password=os.environ["TA_REMOTE_PASSWORD"],
    database=os.environ["TA_REMOTE_DB"],
    ssl={"ca": os.environ.get("TA_REMOTE_CA", certifi.where())},
    cursorclass=pymysql.cursors.DictCursor,
)
s, d = src.cursor(), dst.cursor()
d.execute("SET FOREIGN_KEY_CHECKS=0")

for t in TABLES:
    s.execute(f"SHOW TABLES LIKE '{t}'")
    if not s.fetchone():
        continue
    s.execute(f"SHOW CREATE TABLE `{t}`")
    ddl = s.fetchone()["Create Table"]
    d.execute(f"DROP TABLE IF EXISTS `{t}`")
    d.execute(ddl)
    s.execute(f"SELECT * FROM `{t}`")
    rows = s.fetchall()
    if rows:
        cols = list(rows[0].keys())
        sql = f"INSERT INTO `{t}` ({','.join('`'+c+'`' for c in cols)}) VALUES ({','.join(['%s']*len(cols))})"
        d.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
    print(f"{t}: {len(rows)} rows")

d.execute("SET FOREIGN_KEY_CHECKS=1")
dst.commit()
print("done")
