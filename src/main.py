import numpy as np
import pandas as pd
import matplotlib as plt

DATA_PATH = '../data/sdss_100k.csv'

def main():
    data = pd.read_csv(DATA_PATH)
    print(data.head()[['rowc', 'colc', 'ra', 'field', 'fieldid', 'dec']])

if __name__ == "__main__":
    main()