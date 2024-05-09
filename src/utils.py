import matplotlib.pyplot as plt
import numpy as np

def splitView(view, values, data):
    _, measures, _ = view
    # m = [m1, m2, ...]
    # f = [f1, f2, ...]
    # targetVecs = [ f1(m1): { a1: v1, a2: v2, ... }, f2(m2): { } ]
    targetVecs = [ { k: 1e-5 for k in values } for _ in range(len(measures)) ]
    referenceVecs = [ { k: 1e-5 for k in values } for _ in range(len(measures)) ]
    for row in data:
        # Target Rows
        attrVal = row[0]
        if row[1] == 1:
            for i in range(2, len(row)):
                targetVecs[i - 2][attrVal] = float(max(row[i], 1e-5))
        # Reference Rows
        else:
            for i in range(2, len(row)):
                referenceVecs[i - 2][attrVal] = float(max(row[i], 1e-5))
    
    return targetVecs, referenceVecs

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

def confidenceInterval(m, n, delta=0.05):
    a = 1 - (m - 1) / n
    b = 2 * np.log(np.log(m + 1e-5))
    c = np.log(np.pi ** 2 / (3 * delta))
    
    return np.sqrt((a * b + c) / (2 * m))

def pruneViews(utilities, views, m, n, k):
    epsilon = confidenceInterval(m, n)

    upperBounds = [utilities[(v[0], v[1][0], v[2][0])] / m + epsilon for view in views]
    topKLowerBound = list(sorted(upperBounds, reverse=True))[k - 1] - 2 * epsilon

    result = []
    for v, u in utilities.items():
        if (u / m + epsilon) >= topKLowerBound:
            result.append(v)
    
    return result

def generateVisualization(view, targetData, referenceData, figName):
    a, [m], [f] = view
    X, targetY = [t[0] for t in targetData], [t[1] for t in targetData]
    referenceY = [r[1] for r in referenceData]

    _X = np.arange(len(X))
    plt.bar(_X - 0.2, targetY, width=0.4)
    plt.bar(_X + 0.2, referenceY, width=0.4)
    plt.xticks(_X, X)
    plt.title(f'{a.capitalize()} vs {f}({m.capitalize()})')
    plt.xlabel(a.capitalize())
    plt.ylabel(f'{f}({m.capitalize()})')
    plt.savefig(f'../visualizations/{figName}.png')