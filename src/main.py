import numpy as np
import heapq, os
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
    utilitySums = { (a, m, f): 0 for a, [m], [f] in views }
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
            for j in range(len(m)):
                target = np.array(list(targetVecs[j].values()))
                reference = np.array(list(referenceVecs[j].values()))
                utilitySums[(a, m[j], f[j])] += entropy(target, reference)
                # break

        # Perform pruning
        print(partitionNum)
        views = pruneViews(utilitySums, views, partitionNum+1, n, k)

    return heapq.nlargest(k, views, lambda v: utilitySums[v[0], v[1][0], v[2][0]])


def main():
    if not os.path.exists('../visualizations/'):
        os.mkdir('../visualizations/')
    db = Database(DB_NAME, TABLE_NAME)
    db.setupTables()

    N, K = 1, 5
    print(rankVisualizations(db, N, K))

    db.closeConnection()

if __name__ == "__main__":
    main()