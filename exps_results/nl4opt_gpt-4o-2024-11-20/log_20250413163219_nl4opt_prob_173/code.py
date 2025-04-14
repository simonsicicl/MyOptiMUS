import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_173/data.json", "r") as f:
    data = json.load(f)

VanCapacity = data["VanCapacity"] # scalar parameter
VanPollution = data["VanPollution"] # scalar parameter
MinibusCapacity = data["MinibusCapacity"] # scalar parameter
MinibusPollution = data["MinibusPollution"] # scalar parameter
MinKids = data["MinKids"] # scalar parameter
MaxMinibuses = data["MaxMinibuses"] # scalar parameter
NumVans = model.addVar(vtype=gp.GRB.INTEGER, name="NumVans")
NumMinibuses = model.addVar(vtype=gp.GRB.INTEGER, name="NumMinibuses")
VanKidsTransported = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VanKidsTransported")
MinibusKidsTransported = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MinibusKidsTransported")

# Add constraint to ensure the total number of kids transported by vans and minibuses is at least MinKids
model.addConstr(VanCapacity * NumVans + MinibusCapacity * NumMinibuses >= MinKids, name="min_kids_transport")

# No additional code needed since NumMinibuses is already defined as non-negative due to its default lower bound (0) in Gurobi.

# The variable NumVans is already defined as non-negative due to being an integer type which is by default >= 0. No additional constraint is necessary.

# Add constraint: The number of kids transported by vans cannot exceed the total capacity of the vans used.
model.addConstr(VanKidsTransported <= NumVans * VanCapacity, name="van_capacity_constraint")

# Add constraint for the total number of kids transported by minibuses 
model.addConstr(MinibusKidsTransported <= NumMinibuses * MinibusCapacity, name="total_kids_transportation")

# Add constraint to ensure no more than MaxMinibuses minibuses can be used
model.addConstr(NumMinibuses <= MaxMinibuses, name="max_minibuses_constraint")

# Add constraint ensuring the total number of kids transported by vans and minibuses meets or exceeds the minimum required
model.addConstr(VanKidsTransported + MinibusKidsTransported >= MinKids, name="min_kids_transport")

# Add constraint ensuring total transported kids meet minimum requirement
model.addConstr(VanKidsTransported + MinibusKidsTransported >= MinKids, name="total_kids_transportation")

# Add constraint to ensure kids transported do not exceed van capacity
model.addConstr(VanKidsTransported <= VanCapacity * NumVans, name="van_capacity_constraint")

# Add constraint to ensure the number of kids transported does not exceed the capacity of the minibuses used
model.addConstr(MinibusKidsTransported <= MinibusCapacity * NumMinibuses, name="kids_transport_capacity")

# Add constraint to ensure the number of minibuses used does not exceed the maximum allowed
model.addConstr(NumMinibuses <= MaxMinibuses, name="max_minibuses_constraint")

# Add non-negativity constraints for all variables
model.addConstr(NumVans >= 0, name="NonNegativity_NumVans")
model.addConstr(NumMinibuses >= 0, name="NonNegativity_NumMinibuses")
model.addConstr(VanKidsTransported >= 0, name="NonNegativity_VanKidsTransported")
model.addConstr(MinibusKidsTransported >= 0, name="NonNegativity_MinibusKidsTransported")

# Set objective
model.setObjective(VanPollution * NumVans + MinibusPollution * NumMinibuses, gp.GRB.MINIMIZE)

# Optimize model
model.optimize()


# Get model status
status = model.status

obj_val = None
# check whether the model is infeasible, has infinite solutions, or has an optimal solution
if status == gp.GRB.INFEASIBLE:
    obj_val = "infeasible"
elif status == gp.GRB.INF_OR_UNBD:
    obj_val = "infeasible or unbounded"
elif status == gp.GRB.UNBOUNDED:
    obj_val = "unbounded"
elif status == gp.GRB.OPTIMAL:
    obj_val = model.objVal
