import sqlite3

conn=sqlite3.connect('../weewx/archive/weewx.sdb')
c=conn.cursor()

c.execute('select * from archive order by dateTime desc')
result=c.fetchone()
