from z3 import *
import time


def max_value(a):
    m = a[0]
    for v in a[1:]:
        m = If(v > m, v, m)
    return m

def arg_max(a):
    m = max_value(a)
    index = 0
    for i in range(len(a)):
        index = If(a[i] == m, i, index)
    return index


def compute_solution(model, used_time, obj, paths):
  #compute the solution starting from the best model found
  couriers = []
  if model != None:
    for path in paths:
      tmp = []
      next = model.evaluate(path[-1]).as_long()
      while next != len(path)-1:
        tmp.append(next+1)
        next = model.evaluate(path[next]).as_long()
      couriers.append(tmp)
  else:
    obj = "N/A"
  return {"time":used_time, "optimal": used_time<300, "obj":obj , "sol": couriers}

def update_time(max_time, start_time):
    return max_time - (time.time() - start_time)