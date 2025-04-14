import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_17/data.json", "r") as f:
    data = json.load(f)

ProfitChair = data["ProfitChair"] # scalar parameter
ProfitDresser = data["ProfitDresser"] # scalar parameter
TotalStain = data["TotalStain"] # scalar parameter
TotalOak = data["TotalOak"] # scalar parameter
StainPerChair = data["StainPerChair"] # scalar parameter
OakPerChair = data["OakPerChair"] # scalar parameter
StainPerDresser = data["StainPerDresser"] # scalar parameter
OakPerDresser = data["OakPerDresser"] # scalar parameter
ChairsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ChairsProduced")
DressersProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DressersProduced")

ChairsProduced.vtype = gp.GRB.INTEGER

DressersProduced.vtype = gp.GRB.INTEGER

# The variable ChairsProduced is already non-negative due to its definition
# No further constraints are needed

# Since DressersProduced is required to be non-negative, we ensure this by setting the lower bound to 0 during the variable creation.
# No need to add an additional constraint as this is handled by the variable type being continuous and the default lower bound is 0.

# In case the variable requires an explicit lower bound change, uncomment the following line:
# model.addConstr(DressersProduced >= 0, name="non_negative_dressers_produced")

# Total stain usage constraint
model.addConstr(StainPerChair * ChairsProduced + StainPerDresser * DressersProduced <= TotalStain, name="total_stain_usage")

# Total oak wood usage for chairs and dressers cannot exceed the total available lengths of oak wood per week
model.addConstr(OakPerChair * ChairsProduced + OakPerDresser * DressersProduced <= TotalOak, name="OakWoodUsage")

# Total stain used for chair production must not exceed the total available stain
model.addConstr(StainPerChair * ChairsProduced <= TotalStain, name="stain_limit")

# Constraint: Total amount of stain used for dressers must not exceed the total stain available
model.addConstr(DressersProduced * StainPerDresser <= TotalStain, name="stain_limit")

# Add constraint for total oak wood used for chairs not exceeding available oak wood
model.addConstr(ChairsProduced * OakPerChair <= TotalOak, name="oak_wood_availability")

# Oak usage constraint for dressers
model.addConstr(OakPerDresser * DressersProduced <= TotalOak, name="oak_usage")

# Define objective function
model.setObjective(ProfitChair * ChairsProduced + ProfitDresser * DressersProduced, gp.GRB.MAXIMIZE)

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
