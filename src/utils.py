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

def pruneViews(utilities, views, m, n, k):
    delta = 0.05
    a = 1 - (m - 1)/n
    b = 2 * np.log(np.log(m + 0.0001))
    c = np.log(np.pi ** 2 / (3 * delta))
    # print(a, b, c)
    epsilon = np.sqrt((a * b + c) / (2 * m))

    # considerd views upper bound
    upperBound = { (view[0], view[1][0], view[2][0]) : utilities[view[0], view[1][0], view[2][0]]/m + epsilon for view in views }

    # list of tuples sorted by upper bound in ascending order
    sortedd = sorted(upperBound.items(), key=lambda view: view[1])

    if len(sortedd) >= k:
        topKViews = sortedd[-k:]

    # get lower bound of the top k views
    lowestTopKUtil = sortedd[0][1] - 2 * epsilon

    for v in utilities.keys():
        if v not in dict(topKViews).keys():
            # if view.upperbound < lowestLowerbound, remove
            if utilities[v]/m + epsilon < lowestTopKUtil:
                views.remove(v)
    
    return views
        
def generateVisualization(view):
    pass