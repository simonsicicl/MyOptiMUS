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
LargePizzas = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargePizzas")
MediumPizzas = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MediumPizzas")

# The variable LargePizzas is already defined as non-negative because Gurobi continuous variables are non-negative by default.

# No additional code needed since the variable MediumPizzas was defined as continuous and inherently satisfies the non-negativity constraint.

# Add constraint to ensure at least MinDough units of dough are used
model.addConstr(
    DoughLarge * LargePizzas + DoughMedium * MediumPizzas >= MinDough,
    name="min_dough_usage"
)

# Add constraint for minimum toppings usage
model.addConstr(ToppingsLarge * LargePizzas + ToppingsMedium * MediumPizzas >= MinToppings, name="min_toppings_usage")

# Add constraint for minimum number of medium pizzas
model.addConstr(MediumPizzas >= MinMedium, name="min_medium_pizzas")

# Add constraint: The number of large pizzas must be at least twice the number of medium pizzas
model.addConstr(LargePizzas >= 2 * MediumPizzas, name="large_vs_medium_pizzas")

# Add minimum dough requirement constraint
model.addConstr(LargePizzas * DoughLarge + MediumPizzas * DoughMedium >= MinDough, name="min_dough_requirement")

# Add minimum toppings requirement constraint
model.addConstr(
    LargePizzas * ToppingsLarge + MediumPizzas * ToppingsMedium >= MinToppings,
    name="min_toppings_requirement"
)

# Add constraint for minimum medium pizzas requirement
model.addConstr(MediumPizzas >= MinMedium, name="min_medium_pizzas")

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
