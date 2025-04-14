import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_239/data.json", "r") as f:
    data = json.load(f)

LimousineCapacity = data["LimousineCapacity"] # scalar parameter
BusCapacity = data["BusCapacity"] # scalar parameter
MinimumPeople = data["MinimumPeople"] # scalar parameter
MinimumLimousinePercentage = data["MinimumLimousinePercentage"] # scalar parameter
LimousinesUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LimousinesUsed")
BusesUsed = model.addVar(vtype=gp.GRB.INTEGER, name="BusesUsed")

# No additional code needed since the variable LimousinesUsed was already defined with a non-negativity constraint.

# No code needed - this constraint is implicitly enforced by the non-negative domain of the variable 'BusesUsed', which is an integer variable.

# Add constraint to ensure at least MinimumPeople are transported
model.addConstr(LimousinesUsed * LimousineCapacity + BusesUsed * BusCapacity >= MinimumPeople, name="minimum_people_constraint")

# Add constraint to enforce MinimumLimousinePercentage
model.addConstr((1 - MinimumLimousinePercentage) * LimousinesUsed >= MinimumLimousinePercentage * BusesUsed, name="minimum_limousine_percentage")

# Add transportation capacity constraint
model.addConstr(
    LimousinesUsed * LimousineCapacity + BusesUsed * BusCapacity >= MinimumPeople,
    name="transportation_capacity"
)

# Update the integrality of LimousinesUsed to align with the problem requirements
LimousinesUsed.vtype = gp.GRB.INTEGER

# Add constraint to ensure minimum percentage of vehicles used are limousines
model.addConstr(
    (1 - MinimumLimousinePercentage) * LimousinesUsed >= MinimumLimousinePercentage * BusesUsed,
    name="min_limousine_percentage_constraint"
)

# Set objective
model.setObjective(LimousinesUsed + BusesUsed, gp.GRB.MINIMIZE)

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
