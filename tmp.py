import sqlite3

sql = sqlite3.connect("sql/tra_stations.sqlite")
cursor = sql.cursor()
cursor.execute("DELETE FROM stations WHERE id = 1001")
sql.commit()
sql.close()