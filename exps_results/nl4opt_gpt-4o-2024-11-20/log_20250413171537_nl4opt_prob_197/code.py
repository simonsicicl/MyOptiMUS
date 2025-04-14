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
NumberOfCanoes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCanoes")
NumberOfDieselBoats = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfDieselBoats")

# Since the variable "NumberOfCanoes" is already defined with non-negativity enforced as it is declared as continuous (vtype=gp.GRB.CONTINUOUS), no additional constraint is needed.

# The constraint is already defined inherently by the non-negative domain of the continuous variable "NumberOfDieselBoats".

# Add constraint: Number of canoes must be at least CanoesPerDieselBoat times the number of diesel boats
model.addConstr(NumberOfCanoes >= CanoesPerDieselBoat * NumberOfDieselBoats, name="canoe_diesel_constraint")

# Add constraint ensuring total number of fish transported meets or exceeds the minimum required amount
model.addConstr(NumberOfCanoes * CanoeCapacity + NumberOfDieselBoats * DieselBoatCapacity >= MinimumFishToTransport, name="minimum_fish_transport")

model.addConstr(
    CanoeCapacity * NumberOfCanoes + DieselBoatCapacity * NumberOfDieselBoats >= MinimumFishToTransport,
    name="minimum_fish_transport_constraint"
)

# Add constraint ensuring minimum canoes for each diesel boat
model.addConstr(
    NumberOfCanoes >= CanoesPerDieselBoat * NumberOfDieselBoats,
    name="min_canoes_per_diesel_boat"
)

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
