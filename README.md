# Multiple couriers problem

## Build the doker container
To build the docker container use the command:   
`docker build . -t cdmo -f Dockerfile`

## Run the container on all the instances and with all the methods
To generate all the results use the command:  
`docker run --mount type=volume,source=results,target=/src/res cdmo 0`

## Run the container with more specific requests for instances, methods and models
To generate more specifc results use the command:  
`docker run --mount type=volume,source=results,target=/src/res cdmo <inst_number> <method> <model>`  
-inst_number is a mandatory parameter. It is an integer between 1 and 21 representing the instance to solve. If 0, then the program will run on all the instances

-method is a string in {cp, sat, smt, mip}. It can be omitted to run the program with all the methods

-model is an integer which specifies a particular configuration of model and solver. It can be used only if a specific method has been selected as well.  
    *CP:  
        1- Gecode base model  
        2- Gecode base LNS  
        3- Gecode LNS Implied constraint  
        4- Gecode LNS Implied and Symmetry breaking constraints on sizes  
        5- Gecode LNS Implied and Symmetry breaking constraints on distances  
        6- Gecode LNS Implied and all Symmetry breaking  
        7- Chuffed base model  
        8- Chuffed base LUBY  
        9- Chuffed Implied constraint  
        10- Chuffed Implied LUBY  
        11- Chuffed Implied and Symmetry breaking constraints on distances   
        12- Chuffed Implied and Symmetry breaking constraints on distances LUBY  
    *SAT \ SMT:  
        1- One solver base  
        2- One solver Implied constraint  
        3- One solver Implied and Symmetry breaking constraints on sizes  
        4- One solver Implied and Symmetry breaking constraints on distances  
        5- One solver Implied and all Symmetry breaking constraints  
        6- One solver all Symmetry breaking constraints  
        7- Two solvers base  
        8- Two solvers Implied constraint  
        9- Two solvers Implied and Symmetry breaking constraints on sizes  
        10- Two solvers Implied and Symmetry breaking constraints on distances  
        11- Two solvers Implied and all Symmetry breaking constraints  
        12- Two solvers all Symmetry breaking constraints  
    *MIP:  
        1- Gurobi base model  
        2- Gurobi with Implied constraint  
        3- Gurobi Implied and symmetry breaking constraints on distances  
        4- Gurobi Implied and symmetry breaking constraints on sizes 
        5- Gurobi Implied and all symmetry breaking constraints  
        6- Highs base model    
        7- Highs with Implied constraint    
        8- Highs Implied and symmetry breaking constraints on distances    
        9- Highs Implied and symmetry breaking constraints on sizes   
        10- Highs Implied and all symmetry breaking constraints   
