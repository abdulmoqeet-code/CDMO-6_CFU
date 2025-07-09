from .bin_numbers import *
from .logic import *
from .utils import *
import time
import numpy as np

    

def symmetry_breaking(m, n, assign_solver, paths_solver, loads, path, l, symmetric, sym_on_sizes, sym_on_dist):
  #symmetry on sizes
  if sym_on_sizes:
    for i in range(m):
      for j in range(i+1, m):
        if l[i] < l[j]:
          assign_solver.add(leq(loads[i], loads[j]))
  #symmetry on distances
  if symmetric and sym_on_dist:
    for i in range(m):
      for j in range(n):
        for k in range(n):
          paths_solver.add(Implies(And(path[i][j][-1], path[i][k][j]), leq(path[i][k], path[i][-1])))

def define_model(m, n, l, implied):
  loads = [[Bool(f"w_{i}_{j}")for j in range(l[i].bit_length())]for i in range(m)]
  #loads_i represent the actual load of courier i in binary

  path = [[[Bool(f"x_{i}_{j}_{k}")for k in range(n+1)]for j in range(n+1)]for i in range(m)]
  #path_ijk = True if courier i goes from item j to item k

  a = [[Bool(f"y_{i}_{j}")for j in range(n)]for i in range(m)]
  #a_ij = True if courier i picks up item j

  digits = None
  if implied:
    digits = max(n-m, 1)
  else:
    digits = max(n-1,1)
  order = [[Bool(f"z_{j}_{k}")for k in range((digits).bit_length())]for j in range(n)]
  #order_j is the binary representation of the position of item j in its path

  return loads, path, a, order

def constraints(assign_solver, paths_solver, m, n, l, path, a, order, loads, bin_l, bin_s, symmetric, implied, sym_on_sizes, sym_on_dist):
  #every courier delivers at least one item
  if implied:
    for i in range(m):
      assign_solver.add(at_least_one(a[i]))

  #every item assigned to one and only one courier
  for j in range(n):
    assign_solver.add(exactly_one([a[i][j] for i in range(m)], f"assignement_{j}"))

  #constraint on couriers maximum capacities
  for i in range(m):
    assign_solver.add((multiple_sum(a[i], bin_s , loads[i], f"load_constraint_{i}")))
    assign_solver.add(leq(loads[i], bin_l[i]))

  #constraints on paths
  for i in range(m):
    paths_solver.add([Not(path[i][j][j])for j in range(n+1)])   #courier cant go from j to j
    #channelling between assignement and paths
    for j in range(n):
      paths_solver.add(Implies(a[i][j], And(exactly_one(path[i][j], f"channelling_from_{i}_{j}"), 
                                      exactly_one([path[i][k][j]for k in range(n+1)],
                                                  f"channelling_to_{i}_{j}"))))
      paths_solver.add(Implies(Not(a[i][j]), And(all_False(path[i][j]),
                                           all_False([path[i][k][j] for k in range(n+1)]))))
      #avoid sub-loops
      for k in range(n):
        paths_solver.add(Implies(path[i][j][k],bin_sum([True], order[j], order[k], f"avoid_loops_{i}_{j}_{k}")[0]))
      paths_solver.add(Implies(path[i][n][j], all_False(order[j])))
    #every courier starts and finishes in origin
    paths_solver.add(Implies(Or(a[i]), And(exactly_one([path[i][-1][j]for j in range(n)], f"{i}_starts"),
                                               exactly_one([path[i][j][-1]for j in range(n)], f"{i}_ends"))))

  symmetry_breaking(m, n, assign_solver, paths_solver,  loads, path, l, symmetric, sym_on_sizes, sym_on_dist)

def linear_sweep(start_time, max_time, assign_solver, paths_solver, D, n, m, path, a, implied):
    #computation of upper and lower bound and their binary representation
    max_values = [max(D[j]) for j in range(len(D))]
    upper_bound = None
    if implied:
      max_values.sort()
      upper_bound = sum(max_values[m-1:])
    else:
      upper_bound = sum(max_values)

    lower_bound = max([D[n][j] + D[j][n] for j in range(n+1)])
    bin_lower_bound = [Bool(f"bin_lower_bound_{z}")for z in range(lower_bound.bit_length())]

    bin_lower_bound = int_to_bin(lower_bound, len(bin_lower_bound))

    #binary representation of the distances between nodes/items
    bin_d = [[[Bool(f"_bin_d_{j}_{k}_{z}")for z in range(D[j][k].bit_length())] for k in range(n+1)]for j in range(n+1)]
    for j in range(n+1):
      for k in range(n+1):
        bin_d[j][k] = int_to_bin(D[j][k], len(bin_d[j][k]))

    bin_upper_bound = [Bool(f"bin_upper_bound_{z}")for z in range(upper_bound.bit_length())]
    bin_upper_bound = int_to_bin(upper_bound, len(bin_upper_bound))
    #variables representing the actual distance travelled by each courier
    dist = [[Bool(f"dist_{i}_{j}")for j in range(upper_bound.bit_length())]for i in range(m)]
    paths_solver.add(at_least_one_geq(dist, bin_lower_bound))
    for i in range(m):
      paths_solver.add(multiple_sum(
      [item for nested_path in path[i] for item in nested_path],
      [item for nested_dist in bin_d for item in nested_dist],dist[i],
      f"distances_{i}"))      
    time_left = update_time(max_time, start_time)
    if time_left<0:
      return compute_solution(None, 300, "N/A", path)
    assign_solver.set("timeout", int(time_left*1000))
    model = None
    while assign_solver.check() == sat:
      #find an assignement with the first solver, injecting the found values into the second
      assign_model = assign_solver.model()
      assign_result = [[assign_model.evaluate(a[i][j])for j in range(n)]for i in range(m)]
      for i in range(m):
        paths_solver.add(leq(dist[i], bin_upper_bound))
      paths_solver.push()
      for i in range(m):
        for j in range(n):
          paths_solver.add(assign_result[i][j] == a[i][j])
      while paths_solver.check() == sat:
        #minimizing the objective for the given assignement
        model = paths_solver.model()
        upper_bound = max(bin_to_int([model.evaluate(bit) for bit in dist[i]]) for i in range(m)) -1
        if upper_bound < lower_bound:
          used_time = time.time() - start_time
          return compute_solution(model, math.floor(used_time), upper_bound+1, path)
        bin_upper_bound = [Bool(f"bin_upper_bound_{z}")for z in range(upper_bound.bit_length())]
        bin_upper_bound = int_to_bin(upper_bound, len(bin_upper_bound)) 
        for i in range(m):
          paths_solver.add(leq(dist[i], bin_upper_bound))
        time_left = update_time(max_time, start_time)
        if time_left<=0:
          return compute_solution(model, 300, upper_bound+1, path)
        paths_solver.set("timeout", int(time_left*1000))
      #add constraint to force the first solver to not repeat assignements in different iteractions
      assign_solver.add(Or([Not(a[i][j]) if assign_result[i][j] else a[i][j] for j in range(n) for i in range(m)]))
      paths_solver.pop()
      time_left = update_time(max_time, start_time)
      if time_left<=0:
        return compute_solution(model, 300, upper_bound+1, path)
      assign_solver.set("timeout", int(time_left*1000))
    used_time = time.time() - start_time
    return compute_solution(model, math.floor(used_time), upper_bound+1, path)


def run_two_solvers(instance, parameters, max_time, queue):
  #initialization of variables and constraints for the solvers
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

  loads, path, a, order = define_model(m,n,l, implied)

  #binary representation of items sizes
  bin_s = [[Bool(f"bin_s_{j}_{z}")for z in range(s[j].bit_length())]for j in range(n)]
  for j in range(n):
    bin_s[j] = int_to_bin(s[j], len(bin_s[j]))

  #binary representation of maximum couriers capacities
  bin_l = [[Bool(f"bin_l_{i}_{z}")for z in range(l[i].bit_length())]for i in range(m)]
  for i in range(m):
    bin_l[i] = int_to_bin(l[i], len(bin_l[i]))

  constraints(assign_solver,paths_solver,  m, n, l, path, a, order, loads, bin_l, bin_s, symmetric, implied, sym_on_sizes, sym_on_dist)
  queue.put(linear_sweep(start_time, max_time, assign_solver, paths_solver, D, n, m, path, a, implied))