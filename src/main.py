import numpy as np
import matplotlib as plt
from utils import *
from db import Database
from scipy.stats import entropy

DATA_PATH = '../data/adult_data.csv'
COLUMNS = [
    'age', 'workclass', 'fnlwgt', 'education', 'education_num', 'marital_status', 'occupation', 'relationship',
    'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week', 'native_country', 'class'
]

DB_NAME = 'project3'
TABLE_NAME = 'census'

ATTRIBUTES = [
    'workclass', 'education', 'occupation', 'relationship', 'race', 'sex', 'native_country', 'class'
]
MEASURES = [ 'age', 'fnlwgt', 'education_num', 'capital_gain', 'capital_loss', 'hours_per_week' ]
AGGREGATES = [ 'AVG', 'SUM', 'COUNT', 'MIN', 'MAX' ]

# n: Number of phases
# k: Top k visualizations will be returned
def rankVisualizations(database: Database, n = 10, k = 5):
    views = generateInitialViews(ATTRIBUTES, MEASURES, AGGREGATES)
    utilities = { (a, m, f): 0 for a, [m], [f] in views }
    for i in range(n):
        partitionNum = i
        combinedViews = []
        for a in ATTRIBUTES:
            currViews = list(filter(lambda v: v[0] == a, views))
            combinedViews.append(combineAggregrates(currViews))

        for view in combinedViews[:1]:
            a, m, f = view
            data = database.getViewCombinedData(view, partitionNum)
            values = database.getValues(a)
            targetVecs, referenceVecs = splitView(view, values, data)
            for i in range(len(m)):
                utilities[(a, m[i], f[i])] += entropy(targetVecs[i].values(), referenceVecs[i].values())

        # Perform pruning
        views = pruneViews(combinedViews)

def main():
    db = Database(DB_NAME, TABLE_NAME)
    db.setupTables()

    N, K = 1, 5
    rankVisualizations(db, N, K)

    db.closeConnection()

if __name__ == "__main__":
    main()