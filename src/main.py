import numpy as np
import pandas as pd
import matplotlib as plt

DATA_PATH = '../data/adult-data.csv'
COLUMNS = [
    'age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship',
    'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'class'
]

def main():
    data = pd.read_csv(DATA_PATH, names=COLUMNS, index_col=False)
    print(data.head())

if __name__ == "__main__":
    main()


# agg = ['count', 'sum', 'avg', 'min', 'max']

# married = [
#     'Married-civ-spouse', 
#     'Married-spouse-absent', 
#     'Married-AF-spouse'
# ]

# unmarried = [
#     'Divorced', 
#     'Never-married', 
#     'Separated', 
#     'Widowed', 
# ]

