import matplotlib.pyplot as plt
import numpy as np


def splitView(view, values, data):
    '''
    Given a view, values, and data, splits the data into target and reference vectors.

    Inputs:
    - view: tuple of the form (a, [m], [f])
    - values: list of values for the attribute a
    - data: list of tuples of the form (attrVal, target, measure1, measure2, ...)

    Outputs:
    - targetVecs: list of dictionaries of the form { attrVal: targetValue }
    - referenceVecs: list of dictionaries of the form { attrVal: referenceValue }
    '''

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
    '''
    Given values and data, formats the data into a dictionary.

    Inputs:
    - values: list of values for the attribute a
    - data: list of tuples of the form (attrVal, value)

    Outputs:
    - result: dictionary of the form { attrVal: value }
    '''

    result = { k: 0 for k in values }
    for row in data:
        result[row[0]] = row[1]

    return result

def generateInitialViews(attrs, measures, aggFuncs):
    '''
    Generates all possible views given the attributes, measures, and aggregate functions.

    Inputs:
    - attrs: list of attributes
    - measures: list of measures
    - aggFuncs: list of aggregate functions

    Outputs:
    - allViews: list of all possible views
    '''

    allViews = []
    for a in attrs:
        for m in measures:
            for f in aggFuncs:
                allViews.append((a, [m], [f]))
    
    return allViews

def combineAggregrates(views: list):
    '''
    Combines multiple views into a single view.

    Inputs:
    - views: list of views of the form (groupByAttr, measures, aggFuncs)

    Outputs:
    - result: tuple of the form (groupByAttr, allMeasures, allAggFuncs)
    '''

    groupByAttr = views[0][0]
    allMeasures, allAggFuncs = [], []
    for view in views:
        groupByAttr, measures, aggFuncs = view
        allMeasures.extend(measures)
        allAggFuncs.extend(aggFuncs)

    return (groupByAttr, allMeasures, allAggFuncs)

def confidenceInterval(M, N, delta=0.05):
    '''
    Computes the confidence interval for the given parameters.

    Inputs:
    - M: number of iterations
    - N: number of partitions
    - delta: confidence level

    Outputs:
    - result: confidence interval
    '''

    a = 1 - (M - 1) / N
    b = 2 * np.log(np.log(M + 1e-5))
    c = np.log(np.pi ** 2 / (3 * delta))
    
    return np.sqrt((a * b + c) / (2 * M))

def pruneViews(utilitySums, views, M, N, K):
    '''
    Prunes views based on the utility sums.

    Inputs:
    - utilitySums: dictionary of utility sums
    - views: list of views
    - M: number of iterations
    - N: number of partitions
    - K: number of views to keep

    Outputs:
    - result: list of pruned views    
    '''

    epsilon = confidenceInterval(M, N)

    upperBounds = [utilitySums[(v[0], v[1][0], v[2][0])] / M + epsilon for v in views]
    topKLowerBound = sorted(upperBounds, reverse=True)[K - 1] - 2 * epsilon

    result = []
    for v, u in utilitySums.items():
        if (u / M + epsilon) >= topKLowerBound:
            result.append((v[0], [v[1]], [v[2]]))
    
    return result

def generateVisualization(view, targetData, referenceData, figName):
    '''
    Generates a visualization for the given view and data.

    Inputs:
    - view: tuple of the form (a, [m], [f])
    - targetData: dictionary of target data
    - referenceData: dictionary of reference data
    - figName: name of the figure

    Outputs:
    - None
    '''

    a, [m], [f] = view
    X, targetY = [t for t in targetData], [t[1] for t in targetData.items()]
    referenceY = [r[1] for r in referenceData.items()]

    _X = np.arange(len(X))
    plt.figure(figsize=(8.0, 6.0))
    plt.bar(_X - 0.2, targetY, width=0.4)
    plt.bar(_X + 0.2, referenceY, width=0.4)
    if a in {'occupation', 'native_country', 'education'}:
        plt.xticks(_X, X, rotation=90)
    else:
        plt.xticks(_X, X)
    plt.title(f'{a.capitalize()} vs {f}({m.capitalize()})')
    plt.xlabel(a.capitalize())
    plt.ylabel(f'{f}({m.capitalize()})')
    plt.legend(['Target (Married)', 'Reference (Unmarried)'])
    plt.savefig(f'../visualizations/{figName}.png')
    plt.clf()