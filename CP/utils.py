import numpy as np

def compute_params(m, distances, implied):
    #function to compute upper_bound, lower_bound and to check if the distance matrix is symmetric
    #the uppper_bound changes according to the presence of the implied constraint
    n = len(distances)
    lower_bound = max([distances[n-1][i] + distances[i][n-1] for i in range(n)])
    max_values = [max(distances[j]) for j in range(n)]
    upper_bound = None
    if implied:
        max_values.sort()
        upper_bound = sum(max_values[m-1:])
    else:
        upper_bound = sum(max_values)
    conv = np.array(distances)
    symmetric = np.array_equal(conv, conv.T)
    return lower_bound, upper_bound, symmetric

def compute_solution(result):
    solution = {}
    solution = {"time":result[0], "optimal": result[0]!=300, "obj": result[1], "sol": result[2]}
    return solution

def build_paths(paths):
    #build the arrays containing the solution starting from the path array of the minizinc model
    sol = []
    for path in paths:
        tmp = []
        next = path[-1]
        while next != len(path):
            tmp.append(next)
            next = path[next-1]
        sol.append(tmp)
    return sol