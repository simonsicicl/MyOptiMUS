import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_197/data.json", "r") as f:
    data = json.load(f)

CanoeCapacity = data["CanoeCapacity"] # scalar parameter
DieselBoatCapacity = data["DieselBoatCapacity"] # scalar parameter
CanoesPerDieselBoat = data["CanoesPerDieselBoat"] # scalar parameter
MinimumFishToTransport = data["MinimumFishToTransport"] # scalar parameter
NumberOfCanoes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCanoes")
NumberOfDieselBoats = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfDieselBoats")

# Add non-negativity constraint for the number of canoes
model.addConstr(NumberOfCanoes >= 0, name="num_canoes_non_negative")

# Constraint: The number of diesel boats must be non-negative
model.addConstr(NumberOfDieselBoats >= 0, name="non_negative_diesel_boats")

# Add canoe constraint: NumberOfCanoes >= CanoesPerDieselBoat * NumberOfDieselBoats
model.addConstr(NumberOfCanoes >= CanoesPerDieselBoat * NumberOfDieselBoats, name="canoe_constraint")

# Total fish transported must be at least the minimum required
model.addConstr(
    NumberOfCanoes * CanoeCapacity + NumberOfDieselBoats * DieselBoatCapacity >= MinimumFishToTransport,
    name="minimum_fish_transportation"
)

# Ensure the total capacity of canoes and diesel boats meets the minimum number of fish to transport to shore
model.addConstr((NumberOfCanoes * CanoeCapacity) + (NumberOfDieselBoats * DieselBoatCapacity) >= MinimumFishToTransport, name="transport_capacity")

# Ensure the minimum number of canoes for each diesel boat according to environmental rules
model.addConstr(NumberOfCanoes >= CanoesPerDieselBoat * NumberOfDieselBoats, name="min_canoes_per_diesel_boat")

# Set objective
model.setObjective(NumberOfCanoes + NumberOfDieselBoats, gp.GRB.MINIMIZE)

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
