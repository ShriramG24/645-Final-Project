import psycopg
from view import View

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
        self.partitions = [f'Partition{i}' for i in range(1, self.numPartitions + 1)]

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
    
    # Returns all data in target dataset (in the partition if specified)
    def getTargetData(self, partitionNum = -1):
        if partitionNum >= 0:
            return self.db.execute(f'''
                SELECT * FROM {self.partitions[partitionNum]} WHERE target = 1;
            ''')
        
        return self.db.execute(f'''
            SELECT * FROM {self.table} WHERE marital_status LIKE 'Married%';
        ''')
    
    # Returns all data in reference dataset (in the partition if specified)
    def getReferenceData(self, partitionNum = -1):
        if partitionNum >= 0:
            return self.db.execute(f'''
                SELECT * FROM {self.partitions[partitionNum]} WHERE target = 0;
            ''')
        
        return self.db.execute(f'''
            SELECT * FROM {self.table} WHERE marital_status NOT LIKE 'Married%';
        ''')
    
    # Returns aggregated view data in target subset of partition
    def getViewTargetData(self, view: View, partitionNum):
        aggCalls = [f'{view.aggFuncs[i]}({view.measures[i]})' for i in range(len(view.measures))]
        return self.db.execute(f'''
            SELECT {view.groupByAttr},{','.join(aggCalls)}
            FROM {self.partitions[partitionNum]}
            WHERE target = 1
            GROUP BY {view.groupByAttr};
        ''')
    
    # Returns aggregated view data in reference subset of partition
    def getViewReferenceData(self, view: View, partitionNum):
        aggCalls = [f'{view.aggFuncs[i]}({view.measures[i]})' for i in range(len(view.measures))]
        return self.db.execute(f'''
            SELECT {view.groupByAttr},{','.join(aggCalls)}
            FROM {self.partitions[partitionNum]}
            WHERE target = 0
            GROUP BY {view.groupByAttr};
        ''')
    
    # Returns aggregated view data in whole partition
    def getViewCombinedData(self, view: View, partitionNum):
        aggCalls = [f'{view.aggFuncs[i]}({view.measures[i]})' for i in range(len(view.measures))]
        return self.db.execute(f'''
            SELECT {view.groupByAttr},{','.join(aggCalls)}
            FROM {self.partitions[partitionNum]}
            GROUP BY {view.groupByAttr};
        ''')

    # Closes DB connection and drops all tables and views
    def closeConnection(self):
        for table in self.partitions:
            self.db.execute(f'''
                DROP VIEW IF EXISTS {table};
            ''')
        self.db.execute('DROP TABLE IF EXISTS census;')
        self.conn.commit()
        self.db.close()