from z3 import *
import time

  
def find_next(model, path):
    for i in range(len(path)):
        if is_true(model.evaluate(path[i])):
            return i
    return None
    

def compute_solution(model, used_time, obj, paths):
    #compute solution starting from the best model found
    couriers = []
    if model != None:
        for path in paths:
            tmp = []
            next = find_next(model, path[-1])
            while next != len(path)-1 and next!=None:
                tmp.append(next+1)
                next = find_next(model, path[next])
            couriers.append(tmp)
    else:
        obj = "N/A"
    return {"time":used_time, "optimal": used_time<300, "obj": obj, "sol": couriers}

def update_time(max_time, start_time):
    return max_time - (time.time() - start_time)


  
 