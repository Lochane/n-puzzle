import numpy as np
from algo import A_star
def solve(matrix):
    print("Input:", matrix)
    algo = A_star()
    path = algo.run()