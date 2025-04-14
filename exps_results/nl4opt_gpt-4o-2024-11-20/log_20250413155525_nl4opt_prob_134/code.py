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
CheesecakeSlices = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CheesecakeSlices")
CaramelCakeSlices = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CaramelCakeSlices")

# No additional code needed since the variable "CheesecakeSlices" is already defined as non-negative (CONTINUOUS variable domain implies non-negative by default unless negative bounds are explicitly set)

# The variable "CaramelCakeSlices" is non-negative due to its default lower bound (0) in Gurobi's `addVar`.

# Add constraint to ensure the number of cheesecake slices is at least CheeseCaramelRatio times the number of caramel cake slices
model.addConstr(CheesecakeSlices >= CheeseCaramelRatio * CaramelCakeSlices, name="cheesecake_caramel_ratio")

# Add minimum caramel cake consumption constraint
model.addConstr(CaramelCakeSlices >= MinCaramel, name="min_caramel_slices")

# Add calorie intake constraint
model.addConstr(
    CheesecakeSlices * CalCheesecake + CaramelCakeSlices * CalCaramelCake <= MaxCalories,
    name="calorie_limit"
)

# Add calorie intake constraint
model.addConstr(CalCheesecake * CheesecakeSlices + CalCaramelCake * CaramelCakeSlices <= MaxCalories, name="calorie_intake_limit")

# Add the minimum caramel cake slices consumption constraint
model.addConstr(CaramelCakeSlices >= MinCaramel, name="min_caramel_constraint")

# Add constraint ensuring the ratio of cheesecake slices to caramel cake slices
model.addConstr(CheesecakeSlices >= CheeseCaramelRatio * CaramelCakeSlices, name="cheesecake_to_caramel_ratio")

# Set objective
model.setObjective(SugarCheesecake * CheesecakeSlices + SugarCaramelCake * CaramelCakeSlices, gp.GRB.MAXIMIZE)

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
