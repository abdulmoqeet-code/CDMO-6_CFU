model_base = r"""

reset;

# PARAMS
param m > 0 integer; #number of couriers
param n > 0 integer; #number of items
param l {1..m} > 0 integer; #couriers load capacity
param s {1..n} > 0 integer; #items size
param D {1..n+1, 1..n+1} >= 0 integer; #distance matrix
param upper_b > 0 integer; #upper_bound
param lower_b > 0 integer; #lower_bound
param M = n;  # Used for big-M constraints linearization
param symmetric binary; #used to exploit the symmetry of the distance matrix

# VARS
var path {1..m, 1..n+1, 1..n+1} binary; #path[i,j,k] == 1 iff courier i goes from j to k
var order {1..n} >= 1, integer; #auxiliary variables used to avoid sub-loops in path
var size {1..m} >=0, integer; #total size carried by each courier
var object >= lower_b, <= upper_b, integer; #objective to minimize

# OBJECTIVE
minimize Objective_function:
    object;

# CONSTRAINTS
# CONSTRAINTS ON PATH
#exactly one time moving from j to another node
s.t. single_dearture {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, j, k] = 1;

#exactly one time reaching j from another node
s.t. single_arrival {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, k, j] = 1;

#always moving from the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. starting_position {i in 1..m}:
    sum{j in 1..n+1} path[i, n+1, j] = 1;

#always returning to the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. ending_position {i in 1..m}:
    sum{j in 1..n+1} path[i, j, n+1] = 1;

#avoid leaving from a node and reaching the same node (except for the depot if there is no implied constraint)
s.t. zero_diagonal {i in 1..m, j in 1..n}:
    path[i, j, j] = 0;

#impose same courier for reaching and leaving a node
s.t. if_reach_then_leave {i in 1..m, j in 1..n}:
    sum{k in 1..n+1} path[i, j, k] = sum{k in 1..n+1} path[i, k, j];

# CONSTRAINTS ON CYCLES
#set the minimum order value for items reached by the depot
s.t. first_position {i in 1..m, j in 1..n}:
    order[j] <= 1 + M * (1 - path[i, n+1, j]);

#if going from j to k, impose an order between j and k
s.t. intermediate_positions_one {i in 1..m, j in 1..n, k in 1..n}:
    order[j] <= order[k] + 1 + M * (1 - path[i, j, k]);

#complementary of the previous one
s.t. intermediate_positions_two {i in 1..m, j in 1..n, k in 1..n}:
    order[j] >= order[k] + 1 - M * (1 - path[i, k, j]);


# CONSTRAINTS ON LOADS
s.t. define_sizes {i in 1..m}:
    size[i] = sum{j in 1..n+1, k in 1..n} path[i, j, k] * s[k];

s.t. capacity {i in 1..m}:
    size[i] <= l[i];

# OBJECTIVE FUNCTION
s.t. obj_function {i in 1..m}:
    sum{j in 1..n+1, k in 1..n+1} path[i, j, k] * D[j, k] <= object;


"""

model_implied = r"""

reset;

# PARAMS
param m > 0 integer; #number of couriers
param n > 0 integer; #number of items
param l {1..m} > 0 integer; #couriers load capacity
param s {1..n} > 0 integer; #items size
param D {1..n+1, 1..n+1} >= 0 integer; #distance matrix
param upper_b > 0 integer; #upper_bound
param lower_b > 0 integer; #lower_bound
param M = n;  # Used for big-M constraints linearization
param symmetric; #used to exploit the symmetry of the distance matrix

# VARS
var path {1..m, 1..n+1, 1..n+1} binary;#path[i,j,k] == 1 iff courier i goes from j to k
var order {1..n} >= 1, integer; #auxiliary variables used to avoid sub-loops in path
var size {1..m} >=0, integer; #total size carried by each courier
var object >= lower_b, <= upper_b, integer; #objective to minimize

# OBJECTIVE
minimize Objective_function:
    object;

# CONSTRAINTS
# CONSTRAINTS ON PATH
#exactly one time moving from j to another node
s.t. single_dearture {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, j, k] = 1;

#exactly one time reaching j from another node
s.t. single_arrival {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, k, j] = 1;

#always moving from the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. starting_position {i in 1..m}:
    sum{j in 1..n} path[i, n+1, j] = 1;

#always returning to the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. ending_position {i in 1..m}:
    sum{j in 1..n} path[i, j, n+1] = 1;

#avoid leaving from a node and reaching the same node (except for the depot if there is no implied constraint)
s.t. zero_diagonal {i in 1..m, j in 1..n+1}:
    path[i, j, j] = 0;

#impose same courier for reaching and leaving a node
s.t. if_reach_then_leave {i in 1..m, j in 1..n}:
    sum{k in 1..n+1} path[i, j, k] = sum{k in 1..n+1} path[i, k, j];

# CONSTRAINTS ON CYCLES
#set the minimum order value for items reached by the depot
s.t. first_position {i in 1..m, j in 1..n}:
    order[j] <= 1 + M * (1 - path[i, n+1, j]);

#if going from j to k, impose an order between j and k
s.t. intermediate_positions_one {i in 1..m, j in 1..n, k in 1..n}:
    order[j] <= order[k] + 1 + M * (1 - path[i, j, k]);

#complementary of the previous one
s.t. intermediate_positions_two {i in 1..m, j in 1..n, k in 1..n}:
    order[j] >= order[k] + 1 - M * (1 - path[i, k, j]);


# CONSTRAINTS ON LOADS
s.t. define_sizes {i in 1..m}:
    size[i] = sum{j in 1..n+1, k in 1..n} path[i, j, k] * s[k];

s.t. capacity {i in 1..m}:
    size[i] <= l[i];

# OBJECTIVE FUNCTION
s.t. obj_function {i in 1..m}:
    sum{j in 1..n+1, k in 1..n+1} path[i, j, k] * D[j, k] <= object;
"""


model_SB_On_Distances = r"""

reset;

# PARAMS
param m > 0 integer; #number of couriers
param n > 0 integer; #number of items
param l {1..m} > 0 integer; #couriers load capacity
param s {1..n} > 0 integer; #items size
param D {1..n+1, 1..n+1} >= 0 integer; #distance matrix
param upper_b > 0 integer; #upper_bound
param lower_b > 0 integer; #lower_bound
param M = n;  # Used for big-M constraints linearization
param symmetric; #used to exploit the symmetry of the distance matrix

# VARS
var path {1..m, 1..n+1, 1..n+1} binary;#path[i,j,k] == 1 iff courier i goes from j to k
var order {1..n} >= 1, integer; #auxiliary variables used to avoid sub-loops in path
var size {1..m} >=0, integer; #total size carried by each courier
var object >= lower_b, <= upper_b, integer; #objective to minimize

# OBJECTIVE
minimize Objective_function:
    object;

# CONSTRAINTS
# CONSTRAINTS ON PATH
#exactly one time moving from j to another node
s.t. single_dearture {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, j, k] = 1;

#exactly one time reaching j from another node
s.t. single_arrival {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, k, j] = 1;

#always moving from the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. starting_position {i in 1..m}:
    sum{j in 1..n} path[i, n+1, j] = 1;

#always returning to the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. ending_position {i in 1..m}:
    sum{j in 1..n} path[i, j, n+1] = 1;

#avoid leaving from a node and reaching the same node (except for the depot if there is no implied constraint)
s.t. zero_diagonal {i in 1..m, j in 1..n+1}:
    path[i, j, j] = 0;

#impose same courier for reaching and leaving a node
s.t. if_reach_then_leave {i in 1..m, j in 1..n}:
    sum{k in 1..n+1} path[i, j, k] = sum{k in 1..n+1} path[i, k, j];

# CONSTRAINTS ON CYCLES
#set the minimum order value for items reached by the depot
s.t. first_position {i in 1..m, j in 1..n}:
    order[j] <= 1 + M * (1 - path[i, n+1, j]);

#if going from j to k, impose an order between j and k
s.t. intermediate_positions_one {i in 1..m, j in 1..n, k in 1..n}:
    order[j] <= order[k] + 1 + M * (1 - path[i, j, k]);

#complementary of the previous one
s.t. intermediate_positions_two {i in 1..m, j in 1..n, k in 1..n}:
    order[j] >= order[k] + 1 - M * (1 - path[i, k, j]);

#SYMMETRY BREAKING ON DISTANCES
s.t. symmetry_breaking_on_distances {i in 1..m : symmetric == 1}:
    sum{j in 1..n} path[i, n+1, j] * j <= sum{j in 1..n} path[i, j, n+1] * j;

# CONSTRAINTS ON LOADS
s.t. define_sizes {i in 1..m}:
    size[i] = sum{j in 1..n+1, k in 1..n} path[i, j, k] * s[k];

s.t. capacity {i in 1..m}:
    size[i] <= l[i];

# OBJECTIVE FUNCTION
s.t. obj_function {i in 1..m}:
    sum{j in 1..n+1, k in 1..n+1} path[i, j, k] * D[j, k] <= object;
"""

model_SB_On_Sizes = r"""

reset;

# PARAMS
param m > 0 integer; #number of couriers
param n > 0 integer; #number of items
param l {1..m} > 0 integer; #couriers load capacity
param s {1..n} > 0 integer; #items size
param D {1..n+1, 1..n+1} >= 0 integer; #distance matrix
param upper_b > 0 integer; #upper_bound
param lower_b > 0 integer; #lower_bound
param M = n;  # Used for big-M constraints linearization
param symmetric binary; #used to exploit the symmetry of the distance matrix

# VARS
var path {1..m, 1..n+1, 1..n+1} binary;#path[i,j,k] == 1 iff courier i goes from j to k
var order {1..n} >= 1, integer; #auxiliary variables used to avoid sub-loops in path
var size {1..m} >=0, integer; #total size carried by each courier
var object >= lower_b, <= upper_b, integer; #objective to minimize

# OBJECTIVE
minimize Objective_function:
    object;

# CONSTRAINTS
# CONSTRAINTS ON PATH
#exactly one time moving from j to another node
s.t. single_dearture {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, j, k] = 1;

#exactly one time reaching j from another node
s.t. single_arrival {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, k, j] = 1;

#always moving from the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. starting_position {i in 1..m}:
    sum{j in 1..n} path[i, n+1, j] = 1;

#always returning to the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. ending_position {i in 1..m}:
    sum{j in 1..n} path[i, j, n+1] = 1;

#avoid leaving from a node and reaching the same node (except for the depot if there is no implied constraint)
s.t. zero_diagonal {i in 1..m, j in 1..n+1}:
    path[i, j, j] = 0;

#impose same courier for reaching and leaving a node
s.t. if_reach_then_leave {i in 1..m, j in 1..n}:
    sum{k in 1..n+1} path[i, j, k] = sum{k in 1..n+1} path[i, k, j];

# CONSTRAINTS ON CYCLES
#set the minimum order value for items reached by the depot
s.t. first_position {i in 1..m, j in 1..n}:
    order[j] <= 1 + M * (1 - path[i, n+1, j]);

#if going from j to k, impose an order between j and k
s.t. intermediate_positions_one {i in 1..m, j in 1..n, k in 1..n}:
    order[j] <= order[k] + 1 + M * (1 - path[i, j, k]);

#complementary of the previous one
s.t. intermediate_positions_two {i in 1..m, j in 1..n, k in 1..n}:
    order[j] >= order[k] + 1 - M * (1 - path[i, k, j]);


# CONSTRAINTS ON LOADS
s.t. define_sizes {i in 1..m}:
    size[i] = sum{j in 1..n+1, k in 1..n} path[i, j, k] * s[k];

s.t. capacity {i in 1..m}:
    size[i] <= l[i];

#SYMMETRY BREAKING ON SIZES
s.t. symmetry_breaking_on_sizes {i in 1..m, j in i+1..m : l[i]<l[j]}:
    size[i] <= size[j];

s.t. symmetry_breaking_on_same_sizes {i in 1..m, j in i+1..m : l[i]==l[j]}:
    sum{k in 1..n} path[i, n+1, k] * k <= sum{k in 1..n} path[j, n+1, k] * k;

# OBJECTIVE FUNCTION
s.t. obj_function {i in 1..m}:
    sum{j in 1..n+1, k in 1..n+1} path[i, j, k] * D[j, k] <= object;

"""

model_implied_Symmetry = r"""

reset;

# PARAMS
param m > 0 integer; #number of couriers
param n > 0 integer; #number of items
param l {1..m} > 0 integer; #couriers load capacity
param s {1..n} > 0 integer; #items size
param D {1..n+1, 1..n+1} >= 0 integer; #distance matrix
param upper_b > 0 integer; #upper_bound
param lower_b > 0 integer; #lower_bound
param M = n;  # Used for big-M constraints linearization
param symmetric binary; #used to exploit the symmetry of the distance matrix

# VARS
var path {1..m, 1..n+1, 1..n+1} binary;#path[i,j,k] == 1 iff courier i goes from j to k
var order {1..n} >= 1, integer; #auxiliary variables used to avoid sub-loops in path
var size {1..m} >=0, integer; #total size carried by each courier
var object >= lower_b, <= upper_b, integer; #objective to minimize

# OBJECTIVE
minimize Objective_function:
    object;

# CONSTRAINTS
# CONSTRAINTS ON PATH
#exactly one time moving from j to another node
s.t. single_dearture {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, j, k] = 1;

#exactly one time reaching j from another node
s.t. single_arrival {j in 1..n}:
    sum{i in 1..m, k in 1..n+1} path[i, k, j] = 1;

#always moving from the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. starting_position {i in 1..m}:
    sum{j in 1..n} path[i, n+1, j] = 1;

#always returning to the depot (without the implied constraint, it could be path[i,n+1,n+1]=1)
s.t. ending_position {i in 1..m}:
    sum{j in 1..n} path[i, j, n+1] = 1;

#avoid leaving from a node and reaching the same node (except for the depot if there is no implied constraint)
s.t. zero_diagonal {i in 1..m, j in 1..n+1}:
    path[i, j, j] = 0;

#impose same courier for reaching and leaving a node
s.t. if_reach_then_leave {i in 1..m, j in 1..n}:
    sum{k in 1..n+1} path[i, j, k] = sum{k in 1..n+1} path[i, k, j];

# CONSTRAINTS ON CYCLES
#set the minimum order value for items reached by the depot
s.t. first_position {i in 1..m, j in 1..n}:
    order[j] <= 1 + M * (1 - path[i, n+1, j]);

#if going from j to k, impose order of j lower than order of k
s.t. intermediate_positions_one {i in 1..m, j in 1..n, k in 1..n}:
    order[j] <= order[k] + 1 + M * (1 - path[i, j, k]);

#complementary of the previous one
s.t. intermediate_positions_two {i in 1..m, j in 1..n, k in 1..n}:
    order[j] >= order[k] + 1 - M * (1 - path[i, k, j]);


# CONSTRAINTS ON LOADS
s.t. sizes {i in 1..m}:
    size[i] = sum{j in 1..n+1, k in 1..n} path[i, j, k] * s[k];

s.t. capacity {i in 1..m}:
    size[i] <= l[i];

#SYMMETRY BREAKING ON SIZES
s.t. symmetry_breaking_on_sizes {i in 1..m, j in i+1..m : l[i]<l[j]}:
    size[i] <= size[j];

s.t. symmetry_breaking_on_same_sizes {i in 1..m, j in i+1..m : l[i]==l[j]}:
    sum{k in 1..n} path[i, n+1, k] * k <= sum{k in 1..n} path[j, n+1, k] * k;

#SYMMETRY BREAKING ON DISTANCES
s.t. symmetry_breaking_on_distances {i in 1..m : symmetric == 1}:
    sum{j in 1..n} path[i, n+1, j] * j <= sum{j in 1..n} path[i, j, n+1] * j;

# OBJECTIVE FUNCTION
s.t. obj_function {i in 1..m}:
    sum{j in 1..n+1, k in 1..n+1} path[i, j, k] * D[j, k] <= object;
"""