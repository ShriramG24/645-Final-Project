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

def pruneViews(views):
    pass

def generateVisualization(view):
    pass