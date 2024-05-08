class View:
    def __init__(self, a: str, m: list, f: list) -> None:
        self.groupByAttr = a
        self.measures = m
        self.aggFuncs = f

    # def klDivergence(self):
    #     '''
    #     calculate the relative entropy from Q to P
        
    #     https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence

    #     Inputs:
    #     - p: 1d numpy array; probability distribution of p
    #     - q: 1d numpy array; probability distribution of q
    #     '''
        
    #     return np.sum(p * np.log(p / q, where = (q != 0)))