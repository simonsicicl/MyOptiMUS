import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_199/data.json", "r") as f:
    data = json.load(f)

C = data["C"] # scalar parameter
P = data["P"] # scalar parameter
Cr = data["Cr"] # scalar parameter
HamburgerCost = data["HamburgerCost"] # scalar parameter
HamburgerCalories = data["HamburgerCalories"] # scalar parameter
HamburgerProtein = data["HamburgerProtein"] # scalar parameter
HamburgerCarbs = data["HamburgerCarbs"] # scalar parameter
WrapCost = data["WrapCost"] # scalar parameter
WrapCalories = data["WrapCalories"] # scalar parameter
WrapProtein = data["WrapProtein"] # scalar parameter
WrapCarbs = data["WrapCarbs"] # scalar parameter
NumHamburgers = model.addVar(vtype=gp.GRB.INTEGER, name="NumHamburgers")
NumWraps = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumWraps")

# Add constraint for minimum total calories from hamburgers and chicken wraps
model.addConstr(NumHamburgers * HamburgerCalories + NumWraps * WrapCalories >= C, "min_calories")

# Add constraint for minimum protein requirement
model.addConstr(HamburgerProtein * NumHamburgers + WrapProtein * NumWraps >= P, name="min_protein_requirement")

# Total carbs from hamburgers and wraps must meet minimum required carbs per worker constraint
model.addConstr(NumHamburgers * HamburgerCarbs + NumWraps * WrapCarbs >= Cr, name="carbs_requirement")

# Since NumHamburgers is already an integer variable, no code is needed to enforce non-negativity
# The Gurobi optimizer inherently ensures that the integer variable is non-negative by default.

# Add constraint to ensure the number of chicken wraps is non-negative
model.addConstr(NumWraps >= 0, name="num_wraps_non_negative")

# Ensure that the total calories provided by hamburgers and wraps meet the minimum required calories
model.addConstr(NumHamburgers * HamburgerCalories + NumWraps * WrapCalories >= C, "calories_requirement")

# Ensure that the total protein provided by hamburgers and wraps meet the minimum required protein
model.addConstr(NumHamburgers * HamburgerProtein + NumWraps * WrapProtein >= P, name="protein_requirement")

# Ensure that the total carbohydrates provided by hamburgers and wraps meet the minimum required carbohydrates
model.addConstr(NumHamburgers * HamburgerCarbs + NumWraps * WrapCarbs >= Cr, name="min_carbohydrates")

# Set objective
model.setObjective(NumHamburgers * HamburgerCost + NumWraps * WrapCost, gp.GRB.MINIMIZE)

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
