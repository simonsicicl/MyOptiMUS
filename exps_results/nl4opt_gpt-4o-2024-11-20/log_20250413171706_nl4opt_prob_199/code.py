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
NumHamburgers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumHamburgers")
NumChickenWraps = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumChickenWraps")

# Add calorie constraint
model.addConstr(
    NumHamburgers * HamburgerCalories + NumChickenWraps * WrapCalories >= C,
    name="calorie_requirement"
)

# Add protein constraint
model.addConstr(NumHamburgers * HamburgerProtein + NumChickenWraps * WrapProtein >= P, name="protein_requirement")

# Add carbohydrate constraints
model.addConstr(
    HamburgerCarbs * NumHamburgers + WrapCarbs * NumChickenWraps >= Cr, 
    name="carbohydrate_minimum"
)

# The variable NumHamburgers already has the non-negativity constraint because it was defined as a continuous variable (default non-negative domain).

# NumChickenWraps is constrained to be non-negative by default as it is defined as a continuous variable with no lower bound change needed.

# Add calories constraint
model.addConstr(NumHamburgers * HamburgerCalories + NumChickenWraps * WrapCalories >= C, name="calories_constraint")

# Add protein constraint
model.addConstr(NumHamburgers * HamburgerProtein + NumChickenWraps * WrapProtein >= P, name="protein_constraint")

# Add carbohydrates constraint
model.addConstr(NumHamburgers * HamburgerCarbs + NumChickenWraps * WrapCarbs >= Cr, name="carbohydrates_constraint")

# Set objective
model.setObjective(NumHamburgers * HamburgerCost + NumChickenWraps * WrapCost, gp.GRB.MINIMIZE)

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
