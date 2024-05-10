import psycopg

class Database:
    def __init__(self, dbname: str, tableName) -> None:
        self.conn = psycopg.connect(
            host='localhost',
            dbname=dbname,
            user='postgres'
        )

        self.db = self.conn.cursor()
        self.table = tableName
        self.numPartitions = 10
        self.partitions = [f'Partition{i}' for i in range(self.numPartitions)]

    # Sets up table and partition views in database
    def setupTables(self):
        with open('setup.sql', 'r') as file:
            self.db.execute(file.read())

        with open('../data/adult-data.csv', 'r') as data:
            with self.db.copy('COPY census FROM STDIN WITH (FORMAT CSV);') as copy:
                while rows := data.read(100):
                    copy.write(rows)
        
        self.db.execute(f'''
            ALTER TABLE census ADD COLUMN id SERIAL PRIMARY KEY;

            CREATE OR REPLACE FUNCTION partition_function(id INT)
            RETURNS INT AS $$
            BEGIN
                RETURN id % 10;
            END;
            $$ LANGUAGE plpgsql;
        ''')

        for i, table in enumerate(self.partitions):
            self.db.execute(f'''
                CREATE VIEW {table} AS
                    SELECT *, CASE WHEN marital_status LIKE 'Married%' THEN 1 ELSE 0 END as target
                    FROM {self.table} WHERE partition_function(id) = {i};
            ''')
        
        self.conn.commit()

    # Returns all data (in the partition if specified)
    def getData(self, partitionNum = -1):
        if partitionNum >= 0:
            self.db.execute(f"SELECT * FROM {self.partitions[partitionNum]};")
        else:
            self.db.execute(f"SELECT * FROM {self.table};")

        return self.db.fetchall()
    
    def getValues(self, attribute):
        self.db.execute(f"SELECT DISTINCT {attribute} FROM {self.table};")
        return list(map(lambda t: t[0], self.db.fetchall()))
    
    # Returns aggregated view in target data
    def getViewTargetData(self, view):
        a, m, f = view
        aggCalls = [f'{f[i]}({m[i]})' for i in range(len(m))]
        self.db.execute(f'''
            SELECT {a},{','.join(aggCalls)}
            FROM {self.table}
            WHERE marital_status LIKE 'Married%'
            GROUP BY {a};
        ''')
        return self.db.fetchall()
    
    # Returns aggregated view in reference data
    def getViewReferenceData(self, view):
        a, m, f = view
        aggCalls = [f'{f[i]}({m[i]})' for i in range(len(m))]
        self.db.execute(f'''
            SELECT {a},{','.join(aggCalls)}
            FROM {self.table}
            WHERE marital_status NOT LIKE 'Married%'
            GROUP BY {a};
        ''')
        return self.db.fetchall()
    
    # Returns aggregated view data in whole partition
    def getViewCombinedData(self, view, partitionNum = 0):
        a, m, f = view
        aggCalls = [f'{f[i]}({m[i]})' for i in range(len(m))]
        self.db.execute(f'''
            SELECT {a},target,{','.join(aggCalls)}
            FROM {self.partitions[partitionNum]}
            GROUP BY {a},target;
        ''')
        return self.db.fetchall()

    # Closes DB connection and drops all tables and views
    def closeConnection(self):
        for table in self.partitions:
            self.db.execute(f'''
                DROP VIEW IF EXISTS {table};
            ''')
        self.db.execute('DROP TABLE IF EXISTS census;')
        self.conn.commit()
        self.db.close()