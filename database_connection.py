import sqlite3

conn = sqlite3.connect("part_mat_data.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS
    sensordata(timestamp str, sensorid int, pm25 float, pm10 float, location str)""")