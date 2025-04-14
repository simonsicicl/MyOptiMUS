import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_198/data.json", "r") as f:
    data = json.load(f)

VanCapacity = data["VanCapacity"] # scalar parameter
CarCapacity = data["CarCapacity"] # scalar parameter
MinimumVoters = data["MinimumVoters"] # scalar parameter
MaxVansRatio = data["MaxVansRatio"] # scalar parameter
NumberOfVans = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfVans")
NumberOfCars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCars")

# The variable "NumberOfVans" is non-negative due to its default lower bound (0) in Gurobi.
# No additional constraint is needed.

# The non-negativity of the continuous variable NumberOfCars is already enforced by default in Gurobi

# Add constraint to ensure voter transport meets or exceeds minimum requirement
model.addConstr(
    NumberOfVans * VanCapacity + NumberOfCars * CarCapacity >= MinimumVoters, 
    name="voter_transport_requirement"
)

# Add constraint that at most MaxVansRatio of the total number of vehicles can be vans
model.addConstr(NumberOfVans * (1 - MaxVansRatio) <= MaxVansRatio * NumberOfCars, name="MaxVansRatio_constraint")

# Add constraint to ensure vehicles can satisfy the minimum voter transport requirement
model.addConstr(
    NumberOfVans * VanCapacity + NumberOfCars * CarCapacity >= MinimumVoters,
    name="minimum_voter_transport_requirement"
)

# Add constraint to enforce the maximum proportion of vans to total vehicles
model.addConstr(NumberOfVans <= MaxVansRatio * (NumberOfVans + NumberOfCars), name="max_vans_ratio")

# Set objective
model.setObjective(NumberOfCars, gp.GRB.MINIMIZE)

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
