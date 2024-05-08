import numpy as np
import matplotlib as plt
from utils import *
from view import View
from db import Database

DATA_PATH = '../data/adult-data.csv'
COLUMNS = [
    'age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship',
    'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'class'
]

DB_NAME = 'project3'
TABLE_NAME = 'census'

ATTRIBUTES = [
    'age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship',
    'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'class'
]
MEASURES = [ 'age', 'fnlwgt', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week' ]
AGGREGATES = [ 'AVG', 'SUM', 'COUNT', 'MIN', 'MAX' ]

# n: Number of phases
# k: Top k visualizations will be returned
def rankVisualizations(n = 10, k = 5):
    views = generateInitialViews(ATTRIBUTES, MEASURES, AGGREGATES)

    for i in range(n):
        partitionNum = i
        combinedViews = []
        for a in ATTRIBUTES:
            currViews = list(filter(lambda v: v.groupByAttr == a, views))
            combinedViews.append(combineAggregrates(currViews))

        # Perform pruning

def main():
    db = Database(DB_NAME, TABLE_NAME)

    N, K = 10, 5
    # print(rankVisualizations(N, K))

if __name__ == "__main__":
    main()