import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_117/data.json", "r") as f:
    data = json.load(f)

FatPerBurger = data["FatPerBurger"] # scalar parameter
CaloriesPerBurger = data["CaloriesPerBurger"] # scalar parameter
FatPerPizzaSlice = data["FatPerPizzaSlice"] # scalar parameter
CaloriesPerPizzaSlice = data["CaloriesPerPizzaSlice"] # scalar parameter
MinFat = data["MinFat"] # scalar parameter
MinCalories = data["MinCalories"] # scalar parameter
CholesterolPerBurger = data["CholesterolPerBurger"] # scalar parameter
CholesterolPerPizzaSlice = data["CholesterolPerPizzaSlice"] # scalar parameter
PizzaBurgerRatio = data["PizzaBurgerRatio"] # scalar parameter
NumberOfBurgers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBurgers")
NumberOfPizzaSlices = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfPizzaSlices")

# Add fat requirement constraint
model.addConstr(
    FatPerBurger * NumberOfBurgers + FatPerPizzaSlice * NumberOfPizzaSlices >= MinFat, 
    name="min_fat_requirement"
)

# Add calorie intake constraint
model.addConstr(
    CaloriesPerBurger * NumberOfBurgers + CaloriesPerPizzaSlice * NumberOfPizzaSlices >= MinCalories, 
    name="calorie_intake_constraint"
)

# Add constraint ensuring the number of pizza slices eaten is at least PizzaBurgerRatio times the number of burgers eaten
model.addConstr(NumberOfPizzaSlices >= PizzaBurgerRatio * NumberOfBurgers, name="pizza_burger_ratio_constraint")

# Non-negativity constraint for the number of burgers
model.addConstr(NumberOfBurgers >= 0, name="non_negativity_burgers")

# The variable "NumberOfPizzaSlices" is non-negative by default (lower bound set to 0), so no additional code is needed to enforce this constraint.

# Add fat requirement constraint
model.addConstr(FatPerBurger * NumberOfBurgers + FatPerPizzaSlice * NumberOfPizzaSlices >= MinFat, name="min_fat_requirement")

# Add calorie requirement constraint
model.addConstr(
    CaloriesPerBurger * NumberOfBurgers + CaloriesPerPizzaSlice * NumberOfPizzaSlices >= MinCalories,
    name="calorie_requirement"
)

# Add a constraint to ensure the ratio of the number of pizza slices to the number of burgers
model.addConstr(NumberOfPizzaSlices == PizzaBurgerRatio * NumberOfBurgers, name="pizza_burger_ratio")

# Set objective
model.setObjective(CholesterolPerBurger * NumberOfBurgers + CholesterolPerPizzaSlice * NumberOfPizzaSlices, gp.GRB.MINIMIZE)

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
