import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_101/data.json", "r") as f:
    data = json.load(f)

ProteinAlpha = data["ProteinAlpha"] # scalar parameter
SugarAlpha = data["SugarAlpha"] # scalar parameter
CaloriesAlpha = data["CaloriesAlpha"] # scalar parameter
ProteinOmega = data["ProteinOmega"] # scalar parameter
SugarOmega = data["SugarOmega"] # scalar parameter
CaloriesOmega = data["CaloriesOmega"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
MinCalories = data["MinCalories"] # scalar parameter
MaxPropOmega = data["MaxPropOmega"] # scalar parameter
AlphaBrandDrinks = model.addVar(vtype=gp.GRB.INTEGER, name="AlphaBrandDrinks")
OmegaBrandDrinks = model.addVar(vtype=gp.GRB.INTEGER, name="OmegaBrandDrinks")

# Since AlphaBrandDrinks is already defined as non-negative by virtue of being an INTEGER variable in gurobi, no constraint is needed.
# The constraint AlphaBrandDrinks >= 0 is implicitly handled by gurobi.

model.addConstr(OmegaBrandDrinks >= 0, "OmegaBrandDrinks_non_negative")

ProteinAlpha = data["ProteinAlpha"] # scalar parameter
ProteinOmega = data["ProteinOmega"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter

# Add constraint for minimum protein requirement
model.addConstr(ProteinAlpha * AlphaBrandDrinks + ProteinOmega * OmegaBrandDrinks >= MinProtein, name="min_protein_requirement")

# Constraint: Total calories from both brands must meet the minimum calorie requirement
model.addConstr(CaloriesAlpha * AlphaBrandDrinks + CaloriesOmega * OmegaBrandDrinks >= MinCalories, "min_calorie_requirement")

# At most MaxPropOmega of the drink should be omega brand
model.addConstr(OmegaBrandDrinks <= MaxPropOmega * (AlphaBrandDrinks + OmegaBrandDrinks), name="OmegaBrandMaxProportion")

# Set objective function
model.setObjective(SugarAlpha * AlphaBrandDrinks + SugarOmega * OmegaBrandDrinks, gp.GRB.MINIMIZE)

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
