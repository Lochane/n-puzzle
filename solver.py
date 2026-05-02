import numpy as np
from algo import Solver
def solve(matrix):
    print("Input:", matrix)
    algo = Solver()
    path = algo.run(matrix, algorithm='A*', heuristic='linear_conflict')
    #* Pour Dani : le dict des algo/heuritic se trouve dans l'init (pour pouvoir voir les noms), le run se trouve à la fin du fichier algo.py et est set par default sur A* et manhattan
    #! Ne pas mettre l'heurisitc zero comme paramètre dispo pour le user, c'est seulement pour uniform et je gère ca dans run