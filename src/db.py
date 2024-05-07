import psycopg
import os

# from dotenv import load_dotenv
# load_dotenv()

conn = psycopg.connect(
    host='localhost',
    dbname='project3',
    user='postgres'
)

db = conn.cursor()

query = '''
        SELECT age, AVG(capital_gain)
        FROM census
        where age > 40
        group by age;
        '''
db.execute(query)
print(db.fetchall())

