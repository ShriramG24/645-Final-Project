import psycopg
from view import View

class Database:
    def __init__(self, dbname: str, tableName) -> None:
        conn = psycopg.connect(
            host='localhost',
            dbname=dbname,
            user='postgres'
        )

        self.db = conn.cursor()
        self.table = tableName
        self.numPartitions = 10
        self.partitions = [f'Partition{i}' for i in range(1, self.numPartitions + 1)]
        self.setupTables()

    # Sets up table and partition views in database
    def setupTables(self):
        with open('setup.sql', 'r') as file:
            self.db.execute(file.read())

        self.db.copy("COPY census FROM '../data/adult-data.csv' WITH CSV;")
        
        for i, table in enumerate(self.partitions):
            self.db.execute(f'''
                CREATE VIEW {table} AS
                    SELECT *, CASE WHEN marital_status LIKE 'Married%' THEN 1 ELSE 0 END as target
                    FROM {self.table} WHERE partition_function(id) = {i};
            ''')

    # Returns all data
    def getData(self, partitionNum = -1):
        if partitionNum >= 0:
            return self.db.execute(f"SELECT * FROM {self.partitions[partitionNum]};")
        
        return self.db.execute(f"SELECT * FROM {self.table};")
    
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
        self.db.close()