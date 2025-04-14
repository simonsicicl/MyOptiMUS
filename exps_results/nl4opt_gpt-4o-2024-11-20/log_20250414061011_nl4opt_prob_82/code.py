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
SmallShops = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallShops")
LargeShops = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeShops")

# Add non-negativity, production target, and workforce limitation constraints

# Non-negativity for small shops
model.addConstr(SmallShops >= 0, name="non_negativity_small_shops")

# Non-negativity for large shops
model.addConstr(LargeShops >= 0, name="non_negativity_large_shops")

# Minimum daily production constraint
model.addConstr(HotDogsSmall * SmallShops + HotDogsLarge * LargeShops >= MinHotDogs, name="minimum_hotdogs_production")

# Worker availability constraint
model.addConstr(WorkersSmall * SmallShops + WorkersLarge * LargeShops <= TotalWorkers, name="worker_availability_constraint")

# No additional code needed because Gurobi variables are non-negative by default unless explicitly defined with lower bounds less than zero.

# Add constraint for minimum daily hot dog production
model.addConstr(HotDogsSmall * SmallShops + HotDogsLarge * LargeShops >= MinHotDogs, name="min_hot_dog_production")

# Add constraint for total workers required by small and large butcher shops
model.addConstr(SmallShops * WorkersSmall + LargeShops * WorkersLarge <= TotalWorkers, name="total_workers_constraint")

# Non-negativity constraint for SmallShops is implicitly ensured by the default lower bound of 0 in gurobipy variables.

# Add total daily production constraint
model.addConstr(HotDogsSmall * SmallShops + HotDogsLarge * LargeShops >= MinHotDogs, name="daily_production_target")

# Add worker requirement constraint
model.addConstr(
    WorkersSmall * SmallShops + WorkersLarge * LargeShops <= TotalWorkers,
    name="worker_requirement"
)

# Set objective
model.setObjective(SmallShops + LargeShops, gp.GRB.MINIMIZE)

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
