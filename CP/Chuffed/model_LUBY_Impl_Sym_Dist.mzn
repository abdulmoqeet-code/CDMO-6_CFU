include "globals.mzn";
include "chuffed.mzn";

%parameters
int: m;  %riders
int: n;  %items
array [1..m] of int: l;  %maximum loads
array [1..n] of int: s;  %sizes
array [1..n+1, 1..n+1] of int: d;  %distances
int: lower_b; %lower_bound
int: upper_b; %upper_bound
bool: symmetric; %used for exploit the symmetry on distances

%variables
array [1..m, 1..n+1] of var 1..n+1: path;%path[i,j] = k with k!=j if courier i goes from j to k
%array of costs
array [1..m] of var int: cost = [sum([d[j, path[i,j]] | j in 1..n+1 where path[i,j]!=j]) | i in 1..m];

%constraints
%subcircuit constraint to avoid sub-loops
constraint forall(i in 1..m)(subcircuit([path[i,j] | j in 1..n+1]));

%each courier has at least one item
constraint forall(i in 1..m)(path[i, n+1] != n+1);
 
%constraints on the value of the objective
constraint max(cost)>=lower_b;
constraint max(cost)<=upper_b;

%constraint on the load capacity of the couriers 
constraint forall(i in 1..m)(sum([s[j] | j in 1..n where path[i,j] != j]) <= l[i]);

%each item assigned only once
constraint forall(j in 1..n)(count(path[..,j], j, m-1));     

%symmetry on distances
constraint symmetric -> forall(i in 1..m)(path[i,n+1] <= arg_max(path[i,1..n])); 

solve :: int_search(path, random_order, indomain_min)
      :: restart_luby(100)minimize max(cost);                                          
 