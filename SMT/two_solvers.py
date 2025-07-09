from .utils import *
from z3 import *
import numpy as np
import time


def define_assign_model(m, n):

    assign = [[Bool(f"assign_{i}_{j}")for j in range(n)]for i in range(m)]
    #assign_i_j true if item j assigned to courier i

    return assign

def define_paths_model(m, n):

    paths = [[Int(f"paths_{i}_{j}")for j in range(n+1)]for i in range(m)]
    #paths_ij = k with k!=j iff courier i goes from j to k

    order = [Int(f"order_{j}")for j in range(n)]
    #auxiliary variables to avoid sub-loops, representing the position of item j in its path

    dists = [Int(f"dists_{i}")for i in range(m)]
    #ditances travelled by each courier

    obj = Int("obj")
    #objective to minimize

    return paths, order, dists, obj


def paths_constraints(paths_solver, m, n, assign, paths, order, dists, obj, D):
    #define the domain of path variables and
    #forcing values in path to be all different for each courier
    for i in range(m):
        paths_solver.add(Distinct(paths[i]))
        for j in range(n+1):
            paths_solver.add(And(paths[i][j]>=0, paths[i][j]<=n))
    
    #constraints linking assign variables to paths variables
    for i in range(m):
        for j in range(n):
            paths_solver.add(If(assign[i][j], paths[i][j]!=j, paths[i][j]==j))
            for k in range(n):
                if j!=k:
                    #ordering between j and k if courier i goes from j to k
                    paths_solver.add(Implies(paths[i][j] == k, order[k]==order[j]+1))
    #ordering for the starting positions
    for j in range(n):
        paths_solver.add(If(Sum([If(paths[i][-1]==j, 1, 0)for i in range(m)])>=1, order[j]==0, order[j]>0))

    #definition of the values of the travelled distances
    for i in range(m):
        paths_solver.add(dists[i] == Sum([If(paths[i][j]==k, D[j][k], 0) 
                                          for j in range(n+1) for k in range(n+1)]))
    #definition of the objective
    paths_solver.add(obj == max_value(dists))


def assign_symmetry_breaking(assign_solver, m, n, l, s, assign, sym_on_sizes):
    #symmetry breaking on sizes and definition of auxiliary size variables to better express them
    if sym_on_sizes:
        sizes = [Int(f"sizes_{i}")for i in range(m)]

        for i in range(m):
            assign_solver.add(sizes[i] == Sum([If(assign[i][j], s[j], 0) for j in range(n)])) 

        for i in range(m):
            for j in range(i+1, m):
                if l[i]<=l[j]:
                    assign_solver.add(sizes[i]<=sizes[j])

def paths_symmetry_breaking(paths_solver, m, paths, symmetric, sym_on_dist):
    #symmetry breaking on distances
    if symmetric and sym_on_dist:
        for i in range(m):
            paths_solver.add(paths[i][-1] <= arg_max(paths[i]))
 

def assign_constraints(assign_solver, m, n, l, s, assign, implied):
    #each courier carries at least one item
    if implied:
        for i in range(m):
            assign_solver.add(Or(assign[i]))

    #each item assigned only once
    for j in range(n):
        assign_solver.add(Sum([If(assign[i][j], 1, 0) for i in range(m)])==1)
    
    #constraint to not exceed couriers maximum capacities
    for i in range(m):
        assign_solver.add(PbLe([(assign[i][j], s[j]) for j in range(n)], l[i])) 


def run_two_solvers(instance, parameters, max_time, queue):
    start_time = time.time()
    m = instance[0]
    n = instance[1]
    l = instance[2]
    s = instance[3]
    D = instance[4]
    conv = np.array(D)
    symmetric = np.array_equal(conv, conv.T)

    implied = parameters[0]
    sym_on_sizes = parameters[1]
    sym_on_dist = parameters[2]

    assign_solver = Solver()
    paths_solver = Solver()

    assign = define_assign_model(m,n)
    assign_constraints(assign_solver, m, n, l, s, assign, implied)

    paths, order, dists, obj = define_paths_model(m, n)
    paths_constraints(paths_solver, m, n, assign, paths, order, dists, obj, D)
    assign_symmetry_breaking(assign_solver, m, n, l, s, assign, sym_on_sizes)
    paths_symmetry_breaking(paths_solver, m, paths, symmetric, sym_on_dist)
    #computation of upper bound and lower bound
    max_values = [max(D[j]) for j in range(len(D))]
    upper_bound = None
    if implied:
        max_values.sort()
        upper_bound = sum(max_values[m-1:])
    else:
        upper_bound = sum(max_values)

    lower_bound = max([D[n][j] + D[j][n] for j in range(n+1)])
    paths_solver.add(obj == max_value(dists))
    paths_solver.add(obj >= lower_bound)

    time_left = update_time(max_time, start_time)
    if time_left <= 0:
        queue.put(compute_solution(None, max_time, "N/A", paths))
    assign_solver.set("timeout", int(time_left*1000))
    model = None
    while assign_solver.check() == sat:
        #finding a suitable assignement with the first solver
        #imposing it to the second solver
        assign_model = assign_solver.model()
        assign_result = [[assign_model.evaluate(assign[i][j])for j in range(n)]for i in range(m)]
        paths_solver.add(obj <= upper_bound)
        paths_solver.push()
        for i in range(m):
            for j in range(n):
                paths_solver.add(assign[i][j] == assign_result[i][j])
        time_left = update_time(max_time, start_time)
        if time_left <= 0:
            queue.put(compute_solution(model, max_time, upper_bound+1, paths))
        paths_solver.set("timeout", int(time_left*1000))
        while paths_solver.check() == sat:
            #minimizing the objective for the imposed assignement
            model = paths_solver.model()
            upper_bound = model[obj].as_long() - 1
            if upper_bound < lower_bound:
                used_time = time.time() - start_time
                queue.put(compute_solution(model, math.floor(used_time), upper_bound+1, paths))
            paths_solver.add(obj <= upper_bound)
            time_left = update_time(max_time, start_time)
            if time_left <= 0:
                queue.put(compute_solution(model, max_time, upper_bound+1, paths))
            paths_solver.set("timeout", int(time_left*1000))
        #forcing the first solver to not repeat assignements already used
        assign_solver.add(Or([Not(assign[i][j]) if assign_result[i][j] else assign[i][j] for j in range(n) for i in range(m) ]))
        paths_solver.pop()
        time_left = update_time(max_time, start_time)
        if time_left <= 0:
            queue.put(compute_solution(model, max_time, upper_bound+1, paths))
        assign_solver.set("timeout", int(time_left*1000))
    used_time = time.time() - start_time
    obj = "N/A" if model is None else upper_bound+1
    queue.put(compute_solution(model, math.floor(used_time),obj, paths))
    
    
