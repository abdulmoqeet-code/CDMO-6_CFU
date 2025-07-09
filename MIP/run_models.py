import time
import numpy as np
from amplpy import AMPL
from .utils import *
import math
from .models import *

models = {1: ["Gurobi_Base", model_base], 2:["Gurobi_Implied", model_implied], 
          3: ["Gurobi_Implied_Sym_on_Distances", model_SB_On_Distances], 
          4: ["Gurobi_Implied_Sym_on_Sizes", model_SB_On_Sizes],
          5: ["Gurobi_Implied_Simmetry", model_implied_Symmetry],
          6: ["Highs_Base", model_base], 7:["Highs_Implied", model_implied], 
          8: ["Highs_Implied_Sym_on_Distances", model_SB_On_Distances], 
          9: ["Highs_Implied_Sym_on_Sizes", model_SB_On_Sizes],
          10: ["Highs_Implied_Simmetry", model_implied_Symmetry]}


def preapre_solver(ampl, additional_params, instance, solver):
    ampl.param["m"] = instance[0]
    ampl.param["n"] = instance[1]
    ampl.param["l"] = instance[2]
    ampl.param["s"] = instance[3]
    ampl.param["D"] = np.ravel(instance[4]).tolist()
    ampl.param["lower_b"] = additional_params[0]
    ampl.param["upper_b"] = additional_params[1]
    ampl.param["symmetric"] = 1 if additional_params[2] else 0
    ampl.setOption("solver", solver)

def run_model(instance, solver, model, time_limit):
    #method to determine and initialize the solver and the instance
    start_time = time.time()
    implied = False
    if "Implied" in solver:
        implied = True
    additional_params = compute_params(instance[0], instance[4], implied)
    ampl = AMPL()
    ampl.eval(model)
    s = None
    if "Gurobi" in solver:
        s = "gurobi"
    else:
        s = "highs"
    preapre_solver(ampl, additional_params, instance, s)
    enc_time = time.time() - start_time
    time_limit = time_limit - enc_time 
    ampl.setOption(f"{s}_options", f"timelim={time_limit} timing=1")
    res_string = ampl.solve(return_output=True)
    result =  ampl.get_value("solve_result")
    objective = round(ampl.get_objective('Objective_function').value())
    if result == "infeasible" or result == "unbounded" or result== "failure" or objective==0:
        return compute_solution((300, "N/A", []))
    if result == "limit":
        used_time = 300
    else:
        used_time = retrieve_solver_time(res_string) + enc_time
    path_df = ampl.get_variable("path").get_values().to_list()
    path = [[[0 for _ in range(instance[1]+1)]for _ in range(instance[1]+1)]for _ in range(instance[0])]
    for i, j, k, value in path_df:
        i, j, k, value = int(i), int(j), int(k), 0 if value <0.5 else 1
        path[i-1][j-1][k-1] = value

    sol = build_paths(path)
    return compute_solution((math.floor(used_time), objective, sol))

def mip(instance, model, time_limit=300):
    #method to run he specified model on the specified instance
    dict = {}
    if model == 0:
        for key in models:
            res = run_model(instance, models[key][0], models[key][1], time_limit)
            dict[models[key][0]] = res
        return dict
    elif model <= len(models):
        res = run_model(instance, models[model][0], models[model][1], time_limit)
        dict[models[model][0]] = res
        return dict
    else:
        print("Wrong model number")

