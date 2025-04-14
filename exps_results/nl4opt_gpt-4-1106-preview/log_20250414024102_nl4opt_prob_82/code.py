import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_82/data.json", "r") as f:
    data = json.load(f)

HotDogsSmall = data["HotDogsSmall"] # scalar parameter
WorkersSmall = data["WorkersSmall"] # scalar parameter
HotDogsLarge = data["HotDogsLarge"] # scalar parameter
WorkersLarge = data["WorkersLarge"] # scalar parameter
MinHotDogs = data["MinHotDogs"] # scalar parameter
TotalWorkers = data["TotalWorkers"] # scalar parameter
NumSmallShops = model.addVar(vtype=gp.GRB.INTEGER, name="NumSmallShops")
NumLargeShops = model.addVar(vtype=gp.GRB.INTEGER, name="NumLargeShops")

# Since NumSmallShops is already a non-negative integer variable, there is no need to add an additional constraint.

# Since NumLargeShops is already a non-negative integer variable by virtue of being of INTEGER type in gurobi, no constraint is needed.
# The constraint NumLargeShops >= 0 is implicitly handled by gurobi.

# Minimum required production constraint for hot dogs
model.addConstr((NumSmallShops * HotDogsSmall + NumLargeShops * HotDogsLarge >= MinHotDogs), name="min_hotdogs_production")

# Add constraint for the total number of workers across small and large shops
model.addConstr(WorkersSmall * NumSmallShops + WorkersLarge * NumLargeShops <= TotalWorkers, name="total_workers_constraint")

# Ensure the daily production meets the minimum required number of hot dogs
model.addConstr(NumSmallShops * HotDogsSmall + NumLargeShops * HotDogsLarge >= MinHotDogs, "min_daily_production")

# Ensure the total number of workers does not exceed the available workers
model.addConstr(NumSmallShops * WorkersSmall + NumLargeShops * WorkersLarge <= TotalWorkers, "workers_constraint")

# Set objective
model.setObjective(NumSmallShops + NumLargeShops, gp.GRB.MINIMIZE)

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
