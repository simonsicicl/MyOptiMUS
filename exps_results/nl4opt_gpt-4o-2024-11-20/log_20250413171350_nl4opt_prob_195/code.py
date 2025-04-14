import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_195/data.json", "r") as f:
    data = json.load(f)

CarrierCapacity = data["CarrierCapacity"] # scalar parameter
OwlCapacity = data["OwlCapacity"] # scalar parameter
MaxOwlPercentage = data["MaxOwlPercentage"] # scalar parameter
TotalTreats = data["TotalTreats"] # scalar parameter
TreatsPerCarrier = data["TreatsPerCarrier"] # scalar parameter
TreatsPerOwl = data["TreatsPerOwl"] # scalar parameter
MinCarrierPigeons = data["MinCarrierPigeons"] # scalar parameter
CarrierPigeons = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CarrierPigeons")
Owls = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Owls")

# Ensure the number of carrier pigeons used is non-negative
model.addConstr(CarrierPigeons >= 0, name="non_negative_carrier_pigeons")

# The variable "Owls" already has the non-negativity constraint because it was defined as a continuous variable in gurobipy. No additional constraints are needed.

model.addConstr(Owls <= (MaxOwlPercentage / (1 - MaxOwlPercentage)) * CarrierPigeons, name="max_owl_percentage")

# Add constraint for total treats used not exceeding available total treats
model.addConstr(
    TreatsPerCarrier * CarrierPigeons + TreatsPerOwl * Owls <= TotalTreats, 
    name="total_treats_constraint"
)

# Add constraint to ensure the number of carrier pigeons used is at least MinCarrierPigeons
model.addConstr(CarrierPigeons >= MinCarrierPigeons, name="min_carrier_pigeons")

# Add constraint for total treats usage
model.addConstr(
    CarrierPigeons * TreatsPerCarrier + Owls * TreatsPerOwl <= TotalTreats, 
    name="total_treats_constraint"
)

# Add owl percentage constraint
model.addConstr(Owls <= MaxOwlPercentage * (CarrierPigeons + Owls), name="owl_percentage_limit")

# Add minimum carrier pigeons constraint
model.addConstr(CarrierPigeons >= MinCarrierPigeons, name="min_carrier_pigeons")

# Set objective
model.setObjective(CarrierPigeons * CarrierCapacity + Owls * OwlCapacity, gp.GRB.MAXIMIZE)

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
