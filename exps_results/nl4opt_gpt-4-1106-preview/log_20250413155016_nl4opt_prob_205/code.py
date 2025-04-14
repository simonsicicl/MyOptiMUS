import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_205/data.json", "r") as f:
    data = json.load(f)

CostNoodles = data["CostNoodles"] # scalar parameter
CaloriesNoodles = data["CaloriesNoodles"] # scalar parameter
ProteinNoodles = data["ProteinNoodles"] # scalar parameter
CostBars = data["CostBars"] # scalar parameter
CaloriesBars = data["CaloriesBars"] # scalar parameter
ProteinBars = data["ProteinBars"] # scalar parameter
MinCalories = data["MinCalories"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
ServingsNoodles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsNoodles")
ServingsBars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsBars")

# Add constraint for minimum calorie intake from noodles and protein bars
calorie_constraint = (CaloriesNoodles * ServingsNoodles) + (CaloriesBars * ServingsBars) >= MinCalories
model.addConstr(calorie_constraint, name="min_calorie_intake")

# Total protein from noodles and protein bars should be at least MinProtein grams
model.addConstr(ProteinNoodles * ServingsNoodles + ProteinBars * ServingsBars >= MinProtein, name="min_protein_intake")

# Constraint for non-negative noodle servings
model.addConstr(ServingsNoodles >= 0, name="noodle_servings_nonneg")

model.addConstr(ServingsBars >= 0, name="non_negative_servings")

# Set objective function
model.setObjective(CostNoodles * ServingsNoodles + CostBars * ServingsBars, gp.GRB.MINIMIZE)

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
