from minizinc import *
from datetime import timedelta
import time
import math
from .utils import *

models = {1: ["Gecode_base", "model_base.mzn"], 2:["Gecode_base_LNS", "model_base_LNS.mzn"], 
          3: ["Gecode_LNS_Implied", "model_LNS_Impl.mzn"], 
          4: ["Gecode_LNS_Implied_Symmetry_on_Sizes", "model_LNS_Impl_Sym_Sizes.mzn"],
          5: ["Gecode_LNS_Implied_Symmetry_on_Distances", "model_LNS_Impl_Sym_Dist.mzn"],
          6: ["Gecode_LNS_Implied_Symmetry", "model_LNS_Impl_Sym.mzn"],  
          7: ["Chuffed_base", "model_base.mzn"],
          8: ["Chuffed_LUBY_base", "model_LUBY_base.mzn"],
          9: ["Chuffed_Implied", "model_Impl.mzn"],
          10: ["Chuffed_LUBY_Implied", "model_LUBY_Impl.mzn"],
          11: ["Chuffed_Implied_Symmetry_on_Distances", "model_Impl_Sym_Dist.mzn"],
          12: ["Chuffed_LUBY_Implied_Symmetry_On_Distances", "model_LUBY_Impl_Sym_Dist.mzn"]}  


def preapre_instance(inst, additional_params, instance):
    #function to set all the values of the parameters of the minizinc model
    inst["m"] = instance[0]
    inst["n"] = instance[1]
    inst["l"] = instance[2]
    inst["s"] = instance[3]
    inst["d"] = instance[4]
    inst["lower_b"] = additional_params[0]
    inst["upper_b"] = additional_params[1]
    inst["symmetric"] = additional_params[2]
    
    
def run_model(instance, model, file_name, max_time):
    #function to initialize the minizinc instance and solve it with the specified model
    #the first 5 seconds are used to solve the instance with the simpler possible model
    #which is more then enough to solve the simpler instances, for which a too complex
    #model make the performances worse
    start_time = time.time()
    implied = False
    if "Implied" in model:
        implied = True
    additional_params = compute_params(instance[0], instance[4], implied)
    trivial_m = None
    m = None
    solver = None
    if "Gecode" in model:
        solver = Solver.lookup("gecode")
        trivial_m = Model(f"CP/Gecode/{models[1][1]}")
        m = Model(f"CP/Gecode/{file_name}")
    else:
        solver = Solver.lookup("chuffed")
        trivial_m = Model(f"CP/Chuffed/{models[9][1]}")
        m = Model(f"CP/Chuffed/{file_name}")
    trivial_inst = Instance(solver, trivial_m)
    inst = Instance(solver, m)
    preapre_instance(inst, additional_params, instance)
    preapre_instance(trivial_inst, additional_params, instance)
    time_limit = max_time - (time.time() - start_time)
    if time_limit <= 0:
        return compute_solution((300, "N/A", []))
    try:
        result = trivial_inst.solve(timeout=timedelta(seconds=min(time_limit,5)))
        if result.status is Status.OPTIMAL_SOLUTION:
            used_time = time.time() - start_time
            paths = result["path"]
            sol = build_paths(paths)
            return compute_solution((math.floor(used_time), result["objective"], sol))
        time_limit = max_time - (time.time()-start_time)    
        result = inst.solve(timeout=timedelta(seconds=time_limit))
        used_time = 300
        if result.status is Status.OPTIMAL_SOLUTION:
            used_time = time.time() - start_time
        elif result.status is Status.UNKNOWN:
            return compute_solution((used_time, "N/A", []))
        paths = result["path"]
        sol = build_paths(paths)
        return compute_solution((math.floor(used_time), result["objective"], sol))
    except MiniZincError as e:
        return compute_solution((300, "N/A", []))

    
def cp(instance, model, time_limit=300):
    #function called to run the cp models; if model = 0, all model ara run on the instance
    dict = {}
    if model == 0:
        for key in models:
           dict[models[key][0]] = run_model(instance, models[key][0], models[key][1], time_limit)
        return dict
    elif model <= len(models):
        dict[models[model][0]] = run_model(instance, models[model][0], models[model][1], time_limit)
        return dict
    else:
        print("Wrong model number")





