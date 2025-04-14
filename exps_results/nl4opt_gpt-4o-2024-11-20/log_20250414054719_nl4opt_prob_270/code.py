import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_270/data.json", "r") as f:
    data = json.load(f)

ProteinSmoothie = data["ProteinSmoothie"] # scalar parameter
CaloriesSmoothie = data["CaloriesSmoothie"] # scalar parameter
ProteinBar = data["ProteinBar"] # scalar parameter
CaloriesBar = data["CaloriesBar"] # scalar parameter
RatioBarsSmoothies = data["RatioBarsSmoothies"] # scalar parameter
MaxCalories = data["MaxCalories"] # scalar parameter
NumBars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumBars")
NumSmoothies = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumSmoothies")

# Add constraint to enforce the ratio between NumBars and NumSmoothies
model.addConstr(NumBars == RatioBarsSmoothies * NumSmoothies, name="ratio_bars_smoothies")

# Add calorie intake constraint
model.addConstr(CaloriesBar * NumBars + CaloriesSmoothie * NumSmoothies <= MaxCalories, name="calorie_intake_constraint")

# The variable NumSmoothies is already defined as non-negative. No additional code is required for this constraint.

# No additional code needed because the variable "NumBars" is already defined as non-negative due to its default lower bound of 0 in Gurobi.

# Add calorie intake constraint
model.addConstr(CaloriesSmoothie * NumSmoothies + CaloriesBar * NumBars <= MaxCalories, name="calorie_intake_limit")

# Add constraint to ensure the ratio of NumBars to NumSmoothies equals RatioBarsSmoothies
model.addConstr(NumBars == RatioBarsSmoothies * NumSmoothies, name="ratio_bars_smoothies_constraint")

# Set objective
model.setObjective(ProteinSmoothie * NumSmoothies + ProteinBar * NumBars, gp.GRB.MAXIMIZE)

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
