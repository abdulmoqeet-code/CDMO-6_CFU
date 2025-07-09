from SAT.run_models import *
from CP.run_models import *
from SMT.run_models import *
from MIP.run_models import *
import json

def read_instances(n):
    #open the specified instance file and compute the parameters
    instance = []
    file = open(f"Instances/inst{n:02}.dat")
    
    l = 0
    distances = []
    for line in file.readlines():
        line = line.strip()
        if l < 2:
            instance.append(int(line))
        elif l < 4:
            tmp = []
            for part in line.split():
                tmp.append(int(part))
            instance.append(tmp)
        else:
            tmp = []
            for part in line.split(" "):
                tmp.append(int(part))
            distances.append(tmp)
        l += 1
    instance.append(distances)
    return instance

def write_result(inst_number, dict, method):
    #write the results in json format
    data = {}
    file_path = f"res/{method}/{inst_number}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file = None
    try:
        file = open(f"res/{method}/{inst_number}.json", "r")
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = {}
    except FileNotFoundError:
        None
    file = open(f"res/{method}/{inst_number}.json", "w")
    for key in dict:
        data[key] = dict[key]
    json.dump(data, file, indent=4)

def run_cp(inst_number, model=0):
    dict = {}
    if inst_number == 0:
        for i in range(1, 22):
            print("Solving: ", i)
            instance = read_instances(i)
            dict = cp(instance, model)
            write_result(i, dict, "CP")
    else:
        instance = read_instances(inst_number)
        dict = cp(instance, model)
        write_result(inst_number, dict, "CP")
    

def run_sat(inst_number, model=0):
    dict = {}
    if inst_number == 0:
        for i in range(1, 22):
            print("Solving: ", i)
            instance = read_instances(i)
            dict = sat_method(instance, model)
            write_result(i, dict, "SAT")
    else:
        instance = read_instances(inst_number)
        dict = sat_method(instance, model)
        write_result(inst_number, dict, "SAT")

def run_smt(inst_number, model=0):
    dict = {}
    if inst_number == 0:
        for i in range(1, 22):
            print("Solving: ", i)
            instance = read_instances(i)
            dict = smt(instance, model)
            write_result(i, dict, "SMT")
    else:
        instance = read_instances(inst_number)
        dict = smt(instance, model)
        write_result(inst_number, dict, "SMT")

def run_mip(inst_number, model=0):
    dict = {}
    if inst_number == 0:
        for i in range(1, 22):
            print("Solving: ", i)
            instance = read_instances(i)
            dict = mip(instance, model)
            write_result(i, dict, "MIP")
    else:
        instance = read_instances(inst_number)
        dict = mip(instance, model)
        write_result(inst_number, dict, "MIP")

def run_one_method(inst_number, method, model=0):
    if method == "cp":
        run_cp(inst_number, model)
    elif method == "sat":
        run_sat(inst_number, model)
    elif method == "smt":
        run_smt(inst_number, model)
    elif method == "mip":
        run_mip(inst_number, model)
    else:
        print("Wrong number of parameters. Consult the readme file")

def run_all_methods_all_models(inst_number):
    if inst_number == 0:
        for i in range(1, 22):
            print("Solving", i,  "with cp")
            run_cp(i)
            print("Solving", i,  "with sat")
            run_sat(i)
            print("Solving", i,  "with smt")
            run_smt(i)
            print("Solving", i,  "with mip")
            run_mip(i)
    else:
        print("Solving", inst_number,  "with cp")
        run_cp(inst_number)
        print("Solving", inst_number,  "with sat")
        run_sat(inst_number)
        print("Solving", inst_number,  "with smt")
        run_smt(inst_number)
        print("Solving", inst_number,  "with mip")
        run_mip(inst_number)

if __name__ == "__main__":
    if len(sys.argv)<2 or len(sys.argv)>4:
        print("Wrong number of parameters. Consult the readme file")
    elif len(sys.argv) == 2:
        run_all_methods_all_models(int(sys.argv[1]))
    elif len(sys.argv) == 3:
        run_one_method(int(sys.argv[1]), sys.argv[2].lower())
    else:
        run_one_method(int(sys.argv[1]), sys.argv[2].lower(), int(sys.argv[3]))
        
        

    

    



        
