from .one_solver import *
from .two_solvers import *
import multiprocessing


models={1: ["Base", (False, False, False)],
        2: ["Implied", (True, False, False)],
        3: ["Implied_Symmetry_On_Sizes", (True, True, False)],
        4: ["Implied_Symmetry_On_Distances", (True, False, True)],
        5: ["Implied_Symmetry", (True, True, True)],
        6: ["Symmetry", (False, True, True)],
        7: ["Two_Solvers_Base", (False, False, False)],
        8: ["Two_Solvers_Implied", (True, False, False)],
        9: ["Two_Solvers_Implied_Symmetry_On_Sizes", (True, True, False)],
        10: ["Two_Solvers_Implied_Symmetry_On_Distances", (True, False, True)],
        11: ["Two_Solvers_Implied_Symmetry", (True, True, True)],
        12: ["Two_Solvers_Symmetry", (False, True, True)]}


def run_model(instance, model, parameters, max_time):
  #method that run the actual solving method inside a timed subprocess to avoid
  #exceeding the time limit due to too high encoding times
  queue = multiprocessing.Queue()
  if "Two_Solvers" in model:
    t = run_two_solvers
  else:
    t = run_one_solver
  process = multiprocessing.Process(target=t, args=(instance, parameters, max_time, queue))
  try:
    process.start()
    res = queue.get(block=True, timeout=max_time+5)
    return res
  except Exception as e:
    return compute_solution(None, 300, "N/A", [])
  finally: 
    process.terminate()
  
  

def sat_method(instance, model, max_time=300):
  #method to run the solve the specified instance with the specified model
  dict = {}
  if model == 0:
    for key in models:
      dict[models[key][0]] = run_model(instance, models[key][0], models[key][1], max_time)
    return dict
  elif model <= len(models):
    dict[models[model][0]] = run_model(instance, models[model][0], models[model][1], max_time)
    return dict
  else:
    print("Wrong model number")

  

  

  



