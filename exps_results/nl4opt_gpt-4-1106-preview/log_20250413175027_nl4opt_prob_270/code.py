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
NumBars = model.addVar(vtype=gp.GRB.INTEGER, name="NumBars")
NumSmoothies = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumSmoothies")

# Constraint to ensure NumBars is exactly RatioBarsSmoothies times NumSmoothies
model.addConstr(NumBars == RatioBarsSmoothies * NumSmoothies, name="bars_to_smoothies_ratio")

# Total calorie intake constraint
model.addConstr(NumBars * CaloriesBar + NumSmoothies * CaloriesSmoothie <= MaxCalories, "calorie_intake_limit")

# The number of smoothies consumed must be non-negative
model.addConstr(NumSmoothies >= 0, name="non_negativity_smoothies")

model.addConstr(NumBars >= 0, name="non_negative_bars")

# Maximum calorie intake constraint
model.addConstr(CaloriesBar * NumBars + CaloriesSmoothie * NumSmoothies <= MaxCalories, name="max_calories")

# Add constraint to maintain the ratio of the quantity of protein bars to smoothies
model.addConstr(NumBars == RatioBarsSmoothies * NumSmoothies, name="ratio_bars_smoothies_constraint")

# Set objective
model.setObjective(ProteinBar * NumBars + ProteinSmoothie * NumSmoothies, gp.GRB.MAXIMIZE)

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
