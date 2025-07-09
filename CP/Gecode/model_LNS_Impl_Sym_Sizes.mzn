include "globals.mzn";
include "gecode.mzn";

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
constraint forall(i in 1..m)(subcircuit([path[i,j] | j in 1..n+1]))::domain_propagation;

%each courier has at least one item
constraint forall(i in 1..m)(path[i, n+1] != n+1)::domain_propagation;
 
 %constraints on the value of the objective
constraint max(cost)>=lower_b::domain_propagation;
constraint max(cost)<=upper_b::domain_propagation;

%constraint on the load capacity of the couriers
constraint forall(i in 1..m)(sum([s[j] | j in 1..n where path[i,j] != j]) <= l[i])::domain_propagation;

%each item assigned only once
constraint forall(j in 1..n)(count(path[..,j], j, m-1))::domain_propagation;  

%symmetry in sizes
constraint forall(i in 1..m, k in i+1..m)(l[i]==l[k]->path[i,n+1]<path[k,n+1])::domain_propagation;
constraint forall(i in 1..m, k in i+1..m)(l[i]<l[k]->sum([s[j] | j in 1..n where path[i,j] != j]) <=
                                                sum([s[j] | j in 1..n where path[k,j] != j]))::domain_propagation;
 

solve :: int_search(path, dom_w_deg, indomain_random)
      :: restart_luby(100)
      :: relax_and_reconstruct(array1d(path), 80)minimize max(cost);                                          
 