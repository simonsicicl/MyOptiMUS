import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_235/data.json", "r") as f:
    data = json.load(f)

TotalResin = data["TotalResin"] # scalar parameter
ResinMolar = data["ResinMolar"] # scalar parameter
ResinCanine = data["ResinCanine"] # scalar parameter
PainKillerMolar = data["PainKillerMolar"] # scalar parameter
PainKillerCanine = data["PainKillerCanine"] # scalar parameter
MinCaninePercentage = data["MinCaninePercentage"] # scalar parameter
MinMolars = data["MinMolars"] # scalar parameter
NumMolars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumMolars")
NumCanines = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumCanines")
TotalCavities = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalCavities")

# Add constraint to ensure total resin used does not exceed available resin
model.addConstr(NumMolars * ResinMolar + NumCanines * ResinCanine <= TotalResin, name="resin_limit")

# Add constraint: At least MinCaninePercentage of cavities filled must be canines
model.addConstr(NumCanines >= (MinCaninePercentage * NumMolars) / (1 - MinCaninePercentage), name="canine_min_percentage")

# Add the constraint that at least MinMolars molars must be filled
model.addConstr(NumMolars >= MinMolars, name="min_molars_filled")

# The non-negativity of the continuous variable NumMolars is already enforced by default in Gurobi

# Add non-negativity constraint for NumCanines
model.addConstr(NumCanines >= 0, name="non_negativity_NumCanines")

# Add constraint to ensure total resin used does not exceed available resin
model.addConstr(ResinMolar * NumMolars + ResinCanine * NumCanines <= TotalResin, name="resin_usage_limit")

# Add constraint ensuring at least the minimum number of molars filled
model.addConstr(NumMolars >= MinMolars, name="min_molars_constraint")

# Add constraint to ensure a minimum percentage of filled cavities are canines
model.addConstr(NumCanines >= MinCaninePercentage * TotalCavities, name="min_canine_percentage")

# Add constraint to ensure TotalCavities equals the sum of NumMolars and NumCanines
model.addConstr(TotalCavities == NumMolars + NumCanines, name="TotalCavities_balance")

# Set objective
model.setObjective(PainKillerMolar * NumMolars + PainKillerCanine * NumCanines, gp.GRB.MINIMIZE)

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
