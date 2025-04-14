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
NumberOfVans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfVans")
NumberOfMinibuses = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMinibuses")

# Define the constraint for minimum required number of kids to transport
model.addConstr(VanCapacity * NumberOfVans + MinibusCapacity * NumberOfMinibuses >= MinKids, name="min_kids_transport")

model.addConstr(NumberOfMinibuses >= 0, "minibuses_non_negative")

# Since NumberOfVans is already defined as a non-negative integer variable, no additional constraint is needed
# The non-negativity constraint is inherently applied by the variable type definition

NumberOfVans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfVans")
VanCapacity = data["VanCapacity"] # assuming data dictionary is given and has the capacity value
MinKids = data["MinKids"] # assuming data dictionary is given and has the minimum kids value

# Constraint for the capacity of vans in transporting kids
model.addConstr(NumberOfVans * VanCapacity >= MinKids, name="van_capacity_constraint")

# Capacity constraint for kids transportation with minibuses
model.addConstr(NumberOfMinibuses * MinibusCapacity >= MinKids, name="minibus_capacity_constraint")

# Add constraint for the maximum number of minibuses used
model.addConstr(NumberOfMinibuses <= MaxMinibuses, "max_minibuses_constraint")

# Minibuses constraint: The number of minibuses used cannot exceed the maximum number of minibuses allowed
model.addConstr(NumberOfMinibuses <= MaxMinibuses, "minibus_limit")

# Ensure the total capacity of vans and minibuses is sufficient to transport at least the minimum number of kids
model.addConstr(VanCapacity * NumberOfVans + MinibusCapacity * NumberOfMinibuses >= MinKids, "CapacityForKids")

# Limit the number of minibuses used constraint
model.addConstr(NumberOfMinibuses <= MaxMinibuses, name="max_minibuses_constraint")

# Set objective
model.setObjective(VanPollution * NumberOfVans + MinibusPollution * NumberOfMinibuses, gp.GRB.MINIMIZE)

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
