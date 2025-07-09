import numpy as np
import re

def retrieve_solver_time(result):
    #retrieve just the time used by the solver to actually find a solution
    #ignoring post processing time use to return the solution already found and
    #deallocate all the resources 
    match = re.search(r'Solver time = (\d+\.\d+)s', result)
    if match != None:
        return float(match.group(1))
    return None

def compute_params(m, distances, implied):
    #compute upper_bound, lower_bound and check if the distance matrix is symmetric
    #upper_bound changes according to the presence of the implied constraint
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
    return {"time":result[0], "optimal": result[0]!=300, "obj": result[1], "sol": result[2]}

def find_next(row):
    for i in range(len(row)):
        if row[i] == 1:
            return i
    return None

def build_paths(paths):
    #build the solution starting from the values of path returned by the solver
    sol = []
    for path in paths:
        tmp = []
        next = find_next(path[-1])
        while next != len(path)-1 and next!=None:
            tmp.append(next+1)
            next = find_next(path[next])
        sol.append(tmp)
    return sol