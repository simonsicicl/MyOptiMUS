import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_238/data.json", "r") as f:
    data = json.load(f)

DoughLarge = data["DoughLarge"] # scalar parameter
ToppingsLarge = data["ToppingsLarge"] # scalar parameter
TimeLarge = data["TimeLarge"] # scalar parameter
DoughMedium = data["DoughMedium"] # scalar parameter
ToppingsMedium = data["ToppingsMedium"] # scalar parameter
TimeMedium = data["TimeMedium"] # scalar parameter
MinDough = data["MinDough"] # scalar parameter
MinToppings = data["MinToppings"] # scalar parameter
MinMedium = data["MinMedium"] # scalar parameter
LargePizzas = model.addVar(vtype=gp.GRB.INTEGER, name="LargePizzas")
MediumPizzas = model.addVar(vtype=gp.GRB.INTEGER, name="MediumPizzas")
TotalBakingTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalBakingTime")

# Since LargePizzas is already a non-negative integer variable, there is no need to add an additional constraint.
# The definition of LargePizzas as a non-negative integer inherently ensures that it cannot be negative.

model.addConstr(MediumPizzas >= 0, name="non_negativity_medium_pizzas")

# At least MinDough units of dough must be used constraint
model.addConstr(DoughLarge * LargePizzas + DoughMedium * MediumPizzas >= MinDough, name="MinDoughConstraint")

# At least MinToppings units of toppings must be used constraint
model.addConstr(ToppingsLarge * LargePizzas + ToppingsMedium * MediumPizzas >= MinToppings, "MinToppingsConstraint")

# At least MinMedium medium pizzas must be made
model.addConstr(MediumPizzas >= MinMedium, name="min_medium_pizzas")

# Add constraint for large pizzas to be at least twice the number of medium pizzas
model.addConstr(LargePizzas >= 2 * MediumPizzas, name="large_pizzas_at_least_twice_medium")

# Set objective
model.setObjective(LargePizzas * TimeLarge + MediumPizzas * TimeMedium, gp.GRB.MINIMIZE)

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
