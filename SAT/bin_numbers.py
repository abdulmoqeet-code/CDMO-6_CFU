from z3 import *

def int_to_bin(a, digits):
  #conversion from integer to an array of boolean 
  return [(a%(2**(i+1)) // 2**i)==1 for i in range(digits-1,-1,-1)]

def bin_to_int(a):
    #conversion from array of boolean to integer
    return sum(2**(len(a)-i-1) for i in range(len(a)) if is_true(a[i]))

def leq_same(a, b):
    #check a <= b assuming a and b are binary numbers with the same number of digits
    if len(a) == 1:
        return Or(a[0]==b[0], And(Not(a[0]), b[0]))
    else:
        return Or(And(Not(a[0]), b[0]),
                  And(a[0]==b[0], leq_same(a[1:], b[1:])))
    
def leq(a,b):
  #check a<= b assuming a and b are binary numbers possibly with different number of digits
  if len(a) == len(b):
    return leq_same(a,b)
  elif len(a) < len(b):
    diff = len(b)-len(a)
    return Or(Or(b[:diff]), leq_same(a, b[diff:]))
  else:
    diff = len(a)-len(b)
    return And(all_False(a[:diff]), leq_same(a[diff:], b))


def at_least_one_geq(distances,v):
  #method to enforce that at least one value in array distances is graeter of equal than v
  clauses = []
  for dist in distances:
    clauses.append(leq(v, dist))
  return Or(clauses)

def all_eq_same(a,b):
  #check that a==b with a and b binary numbers with the same number of digits
  return And([a[i]==b[i] for i in range(len(a))])

def all_eq(a,b):
  #check a==b with a and b binary numbers possibly with different number of digits
  if len(a) == len(b):
    return all_eq_same(a,b)
  elif len(a)<len(b):
    diff = len(b)-len(a)
    return And(all_False(b[:diff]), all_eq_same(a, b[diff:]))
  else:
    diff = len(a)-len(b)
    return And(all_False(a[:diff]), all_eq_same(a[diff:], b))
  

def all_False(a):
  #chech binary number a==0
  return And([(Not(a[i])) for i in range(len(a))])


def bin_sum_same(a, b, res, name):
  #implement the binary sum between a and b, storing the result into res
  #a and b are supposed to have the same number of digits
  #name is used to generate Bool variables with different names for the z3 solver
  digits = len(a)
  carry = [Bool(f"carry_{name}_{i}") for i in range(digits+1)]
  carry[-1] = False
  clauses = []
  for i in range(digits-1, -1, -1):
    clauses.append(carry[i] == Or(And(a[i], b[i]), And(a[i], carry[i+1]), And(b[i], carry[i+1])))
    clauses.append(res[i] == Xor(Xor(a[i], b[i]), carry[i+1]))
  return And(clauses), carry[0]

def bin_sum(a, b, res, name):
  #implement the binary sum between a and b, storing the result into res
  #a and b are not supposed to have the same number of digits
  #name is used to generate Bool variables with different names for the z3 solver
  if len(res)<len(b) or len(res)<len(a):
    return False, False
  if len(a)<len(b):
    diff = len(b) - len(a)
    partial_res, overflow = bin_sum_same(a, b[diff:], res[diff:], name)
    carry = [Bool(f"carry_diff_length_{i}_{name}") for i in range(diff)] + [overflow]
    clauses = []
    for i in range(diff-1, -1, -1):
      clauses.append(res[i] == Xor(b[i], carry[i+1]))
      clauses.append(carry[i]==And(carry[i+1], b[i]))
    return And(partial_res, And(clauses)), carry[0]
  elif len(a)>len(b):
    return bin_sum(b, a, res, name) 
  else:
    return bin_sum_same(a, b, res, name)
    
    
def multiple_sum(a, s, res, name):
  #implement a serie of binary sums between elements of array s, according to
  #the truth value of the corresponding element in a
  #the final result is stored in res
  #name is used to generate Bool variables with different names for the z3 solver
  digits = len(res)
  inter_res = [[Bool(f"inter_res_{name}_{j}_{k}")for k in range(digits)]for j in range(len(a)-1)]
  inter_res.append(res)
  clauses = []
  clauses.append(And(Implies(a[0], all_eq(s[0], inter_res[0])),
                     Implies(Not(a[0]), all_False(inter_res[0]))))
  for j in range(1, len(inter_res)):
    temp, overflow = bin_sum(s[j], inter_res[j-1], inter_res[j], f"{name}_{j}")
    clauses.append(And(Implies(a[j], And(temp, Not(overflow))),
                       Implies(Not(a[j]), all_eq(inter_res[j], inter_res[j-1]))))
  return And(clauses)
