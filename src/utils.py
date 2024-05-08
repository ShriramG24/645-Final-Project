from view import View

def generateInitialViews(attrs, measures, aggFuncs):
    allViews = []
    for a in attrs:
        for m in measures:
            for f in aggFuncs:
                allViews.append(View(a, [m], [f]))
    
    return allViews

def combineAggregrates(views: list[View]):
    groupByAttr = views[0].groupByAttr
    measures, aggFuncs = [], []
    for view in views:
        measures.extend([m for m in view.measures if m not in measures])
        aggFuncs.extend([f for f in view.aggFuncs if f not in aggFuncs])

    return View(groupByAttr, measures, aggFuncs)

def pruneViews(views):
    pass

def generateVisualization(view: View):
    pass