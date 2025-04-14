import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_86/data.json", "r") as f:
    data = json.load(f)

CoffeePowderPerMocha = data["CoffeePowderPerMocha"] # scalar parameter
MilkPerMocha = data["MilkPerMocha"] # scalar parameter
CoffeePowderPerRegular = data["CoffeePowderPerRegular"] # scalar parameter
MilkPerRegular = data["MilkPerRegular"] # scalar parameter
TotalCoffeePowder = data["TotalCoffeePowder"] # scalar parameter
TotalMilk = data["TotalMilk"] # scalar parameter
TimePerMocha = data["TimePerMocha"] # scalar parameter
TimePerRegular = data["TimePerRegular"] # scalar parameter
MochaToRegularRatio = data["MochaToRegularRatio"] # scalar parameter
Mochas = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Mochas")
RegularCoffees = model.addVar(vtype=gp.GRB.INTEGER, name="RegularCoffees")

# The number of mochas must be non-negative
model.addConstr(Mochas >= 0, name="Mochas_non_negative")

# Add constraint for non-negative number of regular coffees
model.addConstr(RegularCoffees >= 0, name="non_negative_regular_coffees")

# Add constraint to ensure that total coffee powder used doesn't exceed the available amount
model.addConstr(CoffeePowderPerMocha * Mochas + CoffeePowderPerRegular * RegularCoffees <= TotalCoffeePowder, "total_coffee_powder_limit")

# Add constraint for total uses of milk not to exceed TotalMilk
model.addConstr(MilkPerMocha * Mochas + MilkPerRegular * RegularCoffees <= TotalMilk, name="milk_usage")

# Add constraint: Number of mochas must be at least the given ratio times the number of regular coffees
model.addConstr(Mochas >= MochaToRegularRatio * RegularCoffees, name="mocha_ratio_constraint")

# Set objective
model.setObjective(TimePerMocha * Mochas + TimePerRegular * RegularCoffees, gp.GRB.MINIMIZE)

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
