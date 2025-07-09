from .utils import *
from z3 import *
import numpy as np
import time
  

def define_model(m, n):
    path = [[Int(f"path_{i}_{j}")for j in range(n+1)]for i in range(m)]
    #path_i_j = k with k!=j iff couier i goes from j to k

    order = [Int(f"order_{j}")for j in range(n)]
    #order_j = k if j is the kth item delivered by its courier

    dist = [Int(f"dist_{i}")for i in range(m)]
    #distances travelled by each courier


    return path, order, dist

def symmetry_breaking(solver, m, n, l, s, path, symmetric, sym_on_sizes, sym_on_dist):
    #symmetry on sizes
    if sym_on_sizes:
        sizes = [Int(f"sizes_{i}")for i in range(m)]
        for i in range(m):
            solver.add(sizes[i] == sum([If(path[i][j]!=j, s[j],0)for j in range(n)]))
            for j in range(i+1, m):
                if l[i]<l[j]:
                    solver.add(sizes[i]<=sizes[j])
                elif l[i] == l[j]:
                    solver.add(path[i][-1]<=path[j][-1])
    #symmetry in distances
    if symmetric and sym_on_dist:
        for i in range(m):
            solver.add(path[i][-1] <= arg_max(path[i]))


def constraints(solver, path, order, dist, m, n, l, s, D, symmetric, implied, sym_on_sizes, sym_on_dist):
    #imposing the domain of path integer variables
    for i in range(m):
        for j in range(n+1):
            solver.add(And(path[i][j]>=0, path[i][j]<=n))
    
    #imposing the domain of order integer variables
    for j in range(n):
        solver.add(And(order[j]>=0, order[j]<=n))
    
    #each courier carrying at least one item starts in origin
    for i in range(m):
        if implied:
            solver.add(path[i][n] != n)
        else:
            solver.add(Implies(sum([If(path[i][j]!=j, 1, 0) for j in range(n)])>=1, path[i][n]!=n))


    #every item delivered only once
    for j in range(n):
        solver.add(sum([If(path[i][j]!=j,1,0)for i in range(m)])==1)

    #subcircuit constraints
    #all different constraints on the path values of each courier
    for i in range(m):
        solver.add(Distinct(path[i]))
    
    #ordering
    #starting position
    for j in range(n):
        solver.add(If(sum([If(path[i][n]==j, 1, 0)for i in range(m)])==1, order[j]==0, order[j]>0))

    #intermediate positions
    for i in range(m):
        for j in range(n):
            for k in range(n):
                if j!=k:
                    solver.add(Implies(path[i][j]==k, order[k]==order[j]+1))

    #constraint to compute distances
    for i in range(m):
        solver.add(dist[i] == 
                   sum([If(path[i][j]==k, D[j][k],0)for j in range(n+1)for k in range(n+1)if k!=j]))


    #constraint on couriers maximum capacity
    for i in range(m):
        solver.add(sum([If(path[i][j]!=j, s[j],0)for j in range(n)]) <= l[i])

    symmetry_breaking(solver, m, n, l,s, path, symmetric, sym_on_sizes, sym_on_dist)  



def run_one_solver(instance, parameters, max_time, queue):
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

    solver = Solver()

    path, order, dist = define_model(m,n)

    constraints(solver, path, order, dist, m, n, l, s, D, symmetric, implied, sym_on_sizes, sym_on_dist)

    #computation of objective, upper and lower bound
    objective = Int("obj")
    solver.add(objective == max_value(dist))
    max_values = [max(D[j]) for j in range(len(D))]
    upper_bound = None
    if implied:
        max_values.sort()
        upper_bound = sum(max_values[m-1:])
    else:
        upper_bound = sum(max_values)

    lower_bound = max([D[n][j] + D[j][n] for j in range(n+1)])
    solver.add(objective >= lower_bound)

    goal = upper_bound
    solver.push()
    solver.add(objective <= goal)
    time_left = update_time(max_time, start_time)
    if time_left <= 0:
        queue.put(compute_solution(None, max_time, "N/A", path))
    solver.set("timeout", int(time_left*1000))
    model = None
    #implementation of binary sweep
    while(upper_bound - lower_bound) >= 1:
        result = solver.check()
        if result == sat:
            model = solver.model()
            upper_bound = model[objective].as_long()
        elif result == unsat:
            if goal == lower_bound:
                break
            lower_bound = goal
        else:
            obj = "N/A" if model is None else upper_bound
            queue.put(compute_solution(model, 300, obj, path))
        goal = (upper_bound + lower_bound)//2
        solver.pop()
        solver.push()
        solver.add(objective <= goal)
        time_left = update_time(max_time, start_time)
        solver.set("timeout", int(time_left*1000))
    used_time = time.time() - start_time
    obj = "N/A" if model is None else upper_bound
    queue.put(compute_solution(model, math.floor(used_time), obj, path))


