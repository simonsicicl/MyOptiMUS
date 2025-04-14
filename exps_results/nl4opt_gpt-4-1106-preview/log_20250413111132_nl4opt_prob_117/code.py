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
BurgersEaten = model.addVar(vtype=gp.GRB.INTEGER, name="BurgersEaten")
PizzasEaten = model.addVar(vtype=gp.GRB.INTEGER, name="PizzasEaten")

# Add constraint for minimum total fat from burgers and pizzas
model.addConstr(FatPerBurger * BurgersEaten + FatPerPizzaSlice * PizzasEaten >= MinFat, name="min_total_fat")

# Add a constraint for minimum calorie intake
model.addConstr(CaloriesPerBurger * BurgersEaten + CaloriesPerPizzaSlice * PizzasEaten >= MinCalories, "min_calories")

# Add constraint for pizza slices eaten to be at least PizzaBurgerRatio times the burgers eaten
model.addConstr(PizzasEaten >= PizzaBurgerRatio * BurgersEaten, name="pizza_burger_ratio_constraint")

# Add constraint for non-negative burgers eaten
model.addConstr(BurgersEaten >= 0, name="non_negative_burgers")

# Constraint to ensure the number of pizza slices eaten is non-negative
model.addConstr(PizzasEaten >= 0, name="non_negative_pizza_slices")

# Define the objective function
objective = CholesterolPerBurger * BurgersEaten + CholesterolPerPizzaSlice * PizzasEaten
model.setObjective(objective, gp.GRB.MINIMIZE)

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
