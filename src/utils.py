import matplotlib.pyplot as plt
import numpy as np

def splitView(view, values, data):
    _, measures, _ = view
    targetVecs = [ { k: 1e-5 for k in values } for _ in range(len(measures)) ]
    referenceVecs = [ { k: 1e-5 for k in values } for _ in range(len(measures)) ]
    for row in data:
        attrVal = row[0]
        if row[1] == 1:
            for i in range(2, len(row)):
                targetVecs[i - 2][attrVal] = float(max(row[i], 1e-5))
        else:
            for i in range(2, len(row)):
                referenceVecs[i - 2][attrVal] = float(max(row[i], 1e-5))
    
    return targetVecs, referenceVecs

def formatData(values, data):
    result = { k: 0 for k in values }
    for row in data:
        result[row[0]] = row[1]

    return result

def generateInitialViews(attrs, measures, aggFuncs):
    allViews = []
    for a in attrs:
        for m in measures:
            for f in aggFuncs:
                allViews.append((a, [m], [f]))
    
    return allViews

def combineAggregrates(views: list):
    groupByAttr = views[0][0]
    allMeasures, allAggFuncs = [], []
    for view in views:
        groupByAttr, measures, aggFuncs = view
        allMeasures.extend([m for m in measures])
        allAggFuncs.extend([f for f in aggFuncs])

    return (groupByAttr, allMeasures, allAggFuncs)

def confidenceInterval(M, N, delta=0.05):
    a = 1 - (M - 1) / N
    b = 2 * np.log(np.log(M + 1e-5))
    c = np.log(np.pi ** 2 / (3 * delta))
    
    return np.sqrt((a * b + c) / (2 * M))

def pruneViews(utilitySums, views, M, N, K):
    epsilon = confidenceInterval(M, N)

    upperBounds = [utilitySums[(v[0], v[1][0], v[2][0])] / M + epsilon for v in views]
    topKLowerBound = sorted(upperBounds, reverse=True)[:K - 1][-1] - 2 * epsilon

    result = []
    for v, u in utilitySums.items():
        if (u / M + epsilon) >= topKLowerBound:
            result.append((v[0], [v[1]], [v[2]]))
    
    return result

def generateVisualization(view, targetData, referenceData, figName):
    a, [m], [f] = view
    X, targetY = [t for t in targetData], [t[1] for t in targetData.items()]
    referenceY = [r[1] for r in referenceData.items()]

    _X = np.arange(len(X))
    plt.figure(figsize=(8.0, 5.0))
    plt.bar(_X - 0.2, targetY, width=0.4)
    plt.bar(_X + 0.2, referenceY, width=0.4)
    plt.xticks(_X, X)
    plt.title(f'{a.capitalize()} vs {f}({m.capitalize()})')
    plt.xlabel(a.capitalize())
    plt.ylabel(f'{f}({m.capitalize()})')
    plt.savefig(f'../visualizations/{figName}.png')
    plt.clf()