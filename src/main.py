import numpy as np
import heapq, os
from utils import *
from db import Database
from scipy.stats import entropy, wasserstein_distance

DB_NAME = 'project3'
TABLE_NAME = 'census'

ATTRIBUTES = [
    'workclass', 'education', 'occupation', 'relationship', 'race', 'sex', 'native_country', 'class'
]
MEASURES = [ 'age', 'education_num', 'capital_gain', 'capital_loss', 'hours_per_week' ]
AGGREGATES = [ 'AVG', 'SUM', 'COUNT', 'MIN', 'MAX' ]

def euclideanDistance(x, y):
    return np.sqrt(np.linalg.norm(x - y, ord=2))

def topKVisualizations(database: Database, N = 10, K = 5, utility=entropy):
    views = generateInitialViews(ATTRIBUTES, MEASURES, AGGREGATES)
    utilitySums = { (a, m, f): 0 for a, [m], [f] in views }
    for i in range(N):
        combinedViews = []
        for a in ATTRIBUTES:
            currViews = list(filter(lambda v: v[0] == a, views))
            if currViews:
                combinedViews.append(combineAggregrates(currViews))

        for view in combinedViews:
            a, m, f = view
            data = database.getViewCombinedData(view, i)
            values = database.getValues(a)
            targetVecs, referenceVecs = splitView(view, values, data)

            l = []
            for j in range(len(m)):
                target = np.array(list(targetVecs[j].values()))
                reference = np.array(list(referenceVecs[j].values()))
                l.append(utility(target, reference))

            l = np.array(l)
            normalized = list(l-np.min(l))/(np.max(l) - np.min(l) + 1e-5)

            for j in range(len(m)):
                utilitySums[(a, m[j], f[j])] += normalized[j]

        if i > 0:
            views = pruneViews(utilitySums, views, i + 1, N, K)

    return heapq.nlargest(K, views, lambda v: utilitySums[(v[0], v[1][0], v[2][0])])

def main():
    N, K = 10, 5
    if not os.path.exists('../visualizations/'):
        os.mkdir('../visualizations/')
    database = Database(DB_NAME, TABLE_NAME, min(N, 50))
    database.setupTables()

    utilities = [entropy, euclideanDistance, wasserstein_distance]
    for utility in utilities:
        results = topKVisualizations(database, N, K, utility)
        for k, view in enumerate(results):
            values = database.getValues(view[0])
            targetData = formatData(values, database.getViewTargetData(view))
            referenceData = formatData(values, database.getViewReferenceData(view))
            generateVisualization(view, targetData, referenceData, f'Top-{k + 1}-{utility.__name__}.png')

    database.closeConnection()

if __name__ == "__main__":
    main()