import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_186/data.json", "r") as f:
    data = json.load(f)

CapacityCow = data["CapacityCow"] # scalar parameter
CapacityElephant = data["CapacityElephant"] # scalar parameter
MinBricks = data["MinBricks"] # scalar parameter
MaxCowElephantRatio = data["MaxCowElephantRatio"] # scalar parameter
MaxElephantsToCows = data["MaxElephantsToCows"] # scalar parameter
Cows = model.addVar(vtype=gp.GRB.INTEGER, name="Cows")
Elephants = model.addVar(vtype=gp.GRB.INTEGER, name="Elephants")

model.addConstr(Elephants <= Cows, name="elephant_cow_constraint")

# Ensure at most MaxCowElephantRatio cows for each elephant
model.addConstr(Cows <= MaxCowElephantRatio * Elephants, name="max_cow_elephant_ratio")

# Constraint: Total number of bricks carried by cows and elephants meets or exceeds MinBricks
model.addConstr(Cows * CapacityCow + Elephants * CapacityElephant >= MinBricks, name="bricks_requirement")

# Constraint: Number of cows must be non-negative
model.addConstr(Cows >= 0, name="non_negative_cows")

# The number of elephants must be non-negative
model.addConstr(Elephants >= 0, name="elephants_non_negative")

# Ensure minimum number of bricks are transported
model.addConstr(Cows * CapacityCow + Elephants * CapacityElephant >= MinBricks, name="min_bricks")

# Ensure that the number of cows does not exceed the set maximum ratio of cows to elephants
model.addConstr(Cows <= MaxCowElephantRatio * Elephants, name="cow_to_elephant_ratio_constraint")

# Ensure that the number of elephants does not exceed the maximum number allowed relative to the number of cows
model.addConstr(Elephants <= Cows * MaxElephantsToCows, name="elephant_cow_ratio")

# Set objective
model.setObjective(Cows + Elephants, gp.GRB.MINIMIZE)

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
