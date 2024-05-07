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
        SELECT COUNT(*)
        FROM census
        WHERE workclass = 'Private';
        '''
db.execute(query)
print(db.fetchall())

