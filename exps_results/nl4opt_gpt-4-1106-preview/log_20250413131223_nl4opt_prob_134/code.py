import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_134/data.json", "r") as f:
    data = json.load(f)

CalCheesecake = data["CalCheesecake"] # scalar parameter
SugarCheesecake = data["SugarCheesecake"] # scalar parameter
CalCaramelCake = data["CalCaramelCake"] # scalar parameter
SugarCaramelCake = data["SugarCaramelCake"] # scalar parameter
CheeseCaramelRatio = data["CheeseCaramelRatio"] # scalar parameter
MinCaramel = data["MinCaramel"] # scalar parameter
MaxCalories = data["MaxCalories"] # scalar parameter
CheesecakeSlices = model.addVar(vtype=gp.GRB.INTEGER, name="CheesecakeSlices")
CaramelCakeSlices = model.addVar(vtype=gp.GRB.INTEGER, name="CaramelCakeSlices")

# Constraint to ensure the number of cheesecake slices is non-negative
model.addConstr(CheesecakeSlices >= 0, name="nonnegativity_cheesecake_slices")

# Add constraint for non-negativity of caramel cake slices
model.addConstr(CaramelCakeSlices >= 0, name="caramel_cake_nonnegativity")

model.addConstr(CheesecakeSlices >= CheeseCaramelRatio * CaramelCakeSlices, name="CheeseCaramelConstraint")

# At least MinCaramel slices of caramel cake must be eaten
model.addConstr(CaramelCakeSlices >= MinCaramel, name="min_caramel_cake_constraint")

# Add constraint for total calorie intake from all slices not to exceed MaxCalories
model.addConstr(CheesecakeSlices * CalCheesecake + CaramelCakeSlices * CalCaramelCake <= MaxCalories, "max_calorie_intake")

# Define model
model = gp.Model("Cakes")

# Add variables (assuming these are already defined and added to the model)
CheesecakeSlices = model.addVar(vtype=gp.GRB.INTEGER, name="CheesecakeSlices")
CaramelCakeSlices = model.addVar(vtype=gp.GRB.INTEGER, name="CaramelCakeSlices")

# Define parameters
SugarCheesecake = 40  # grams of sugar per slice of cheesecake (assuming data structure is available and this is extraction)
SugarCaramelCake = 50  # grams of sugar per slice of caramel cake (assuming data structure is available and this is extraction)

# Set objective
model.setObjective(CheesecakeSlices * SugarCheesecake + CaramelCakeSlices * SugarCaramelCake, gp.GRB.MAXIMIZE)

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
