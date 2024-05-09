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
    
    # Returns all data in target dataset (in the partition if specified)
    def getTargetData(self, partitionNum = -1):
        if partitionNum >= 0:
            self.db.execute(f'''
                SELECT * FROM {self.partitions[partitionNum]} WHERE target = 1;
            ''')
        else:
            self.db.execute(f'''
                SELECT * FROM {self.table} WHERE marital_status LIKE 'Married%';
            ''')

        return self.db.fetchall()
    
    # Returns all data in reference dataset (in the partition if specified)
    def getReferenceData(self, partitionNum = -1):
        if partitionNum >= 0:
            self.db.execute(f'''
                SELECT * FROM {self.partitions[partitionNum]} WHERE target = 0;
            ''')
        else:
            self.db.execute(f'''
                SELECT * FROM {self.table} WHERE marital_status NOT LIKE 'Married%';
            ''')
        
        return self.db.fetchall()
    
    # Returns aggregated view data in target subset of partition
    def getViewTargetData(self, view, partitionNum):
        aggCalls = [f'{view[2][i]}({view[1][i]})' for i in range(len(view[1]))]
        self.db.execute(f'''
            SELECT {view[0]},{','.join(aggCalls)}
            FROM {self.partitions[partitionNum]}
            WHERE target = 1
            GROUP BY {view[0]};
        ''')
        return self.db.fetchall()
    
    # Returns aggregated view data in reference subset of partition
    def getViewReferenceData(self, view, partitionNum):
        aggCalls = [f'{view[2][i]}({view[1][i]})' for i in range(len(view[1]))]
        self.db.execute(f'''
            SELECT {view[0]},{','.join(aggCalls)}
            FROM {self.partitions[partitionNum]}
            WHERE target = 0
            GROUP BY {view[0]};
        ''')
        return self.db.fetchall()
    
    # Returns aggregated view data in whole partition
    def getViewCombinedData(self, view, partitionNum):
        aggCalls = [f'{view[2][i]}({view[1][i]})' for i in range(len(view[1]))]
        self.db.execute(f'''
            SELECT {view[0]},target,{','.join(aggCalls)}
            FROM {self.partitions[partitionNum]}
            GROUP BY {view[0]},target;
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