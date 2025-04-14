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
NumMolars = model.addVar(vtype=gp.GRB.INTEGER, name="NumMolars")
NumCanines = model.addVar(vtype=gp.GRB.INTEGER, name="NumCanines")

TotalResin = data["TotalResin"] # scalar parameter
ResinMolar = data["ResinMolar"] # scalar parameter
ResinCanine = data["ResinCanine"] # scalar parameter

# Add constraint for total resin usage for all cavities
model.addConstr(ResinMolar * NumMolars + ResinCanine * NumCanines <= TotalResin, name="total_resin_usage")

# Add constraint to ensure at least MinCaninePercentage of cavities filled are canines
model.addConstr(NumCanines >= MinCaninePercentage * (NumMolars + NumCanines), name="min_canine_percentage")

# Add constraint to ensure at least the minimum number of molars are filled
model.addConstr(NumMolars >= MinMolars, name="min_molars_filled")

# Since NumMolars is already defined as an integer variable, no code is needed to enforce non-negativity
# The Gurobi integer variable by default has a lower bound of 0, hence the constraint is implicitly handled

# Add non-negativity constraint for the number of canines to be filled
model.addConstr(NumCanines >= 0, name="nonnegativity_canines")

# Resin usage constraint
model.addConstr(NumMolars * ResinMolar + NumCanines * ResinCanine <= TotalResin, name="resin_usage")

# Add constraint: The number of canines filled must be at least 60 percent of the total cavities filled
model.addConstr(NumCanines >= MinCaninePercentage * (NumMolars + NumCanines), name="canine_to_cavity_ratio")

# Add constraint for minimum number of molars to be filled
model.addConstr(NumMolars >= MinMolars, name="min_molars_filled")

# Define the objective function
model.setObjective(NumMolars * PainKillerMolar + NumCanines * PainKillerCanine, gp.GRB.MINIMIZE)

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
