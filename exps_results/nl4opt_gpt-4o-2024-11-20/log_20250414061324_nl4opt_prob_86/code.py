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
NumberOfMochas = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfMochas")
NumberOfRegularCoffees = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfRegularCoffees")

# Since the variable "NumberOfMochas" is already defined with non-negativity enforced as it is continuous (GRB.CONTINUOUS) by default, no additional constraint is required.

# Add non-negativity constraint for NumberOfRegularCoffees
model.addConstr(NumberOfRegularCoffees >= 0, name="non_negativity_regular_coffees")

# Add constraint to ensure total coffee powder used does not exceed the available amount
model.addConstr(
    CoffeePowderPerMocha * NumberOfMochas + CoffeePowderPerRegular * NumberOfRegularCoffees <= TotalCoffeePowder,
    name="coffee_powder_limit"
)

# Add milk usage constraint
model.addConstr(MilkPerMocha * NumberOfMochas + MilkPerRegular * NumberOfRegularCoffees <= TotalMilk, name="milk_usage_limit")

# Add constraint ensuring the number of mochas is at least MochaToRegularRatio times the number of regular coffees
model.addConstr(NumberOfMochas >= MochaToRegularRatio * NumberOfRegularCoffees, name="mocha_to_regular_ratio")

# Add constraint for coffee powder usage
model.addConstr(CoffeePowderPerMocha * NumberOfMochas + CoffeePowderPerRegular * NumberOfRegularCoffees <= TotalCoffeePowder, 
                name="coffee_powder_limit")

# Add milk usage constraint
model.addConstr(
    MilkPerMocha * NumberOfMochas + MilkPerRegular * NumberOfRegularCoffees <= TotalMilk,
    name="MilkUsageConstraint"
)

# Add minimum ratio constraint for number of mochas
model.addConstr(NumberOfMochas >= MochaToRegularRatio * NumberOfRegularCoffees, name="min_ratio_mochas_regular")

# The variable "NumberOfMochas" is already defined as non-negative because Gurobi continuous variables are non-negative by default.

# The non-negativity constraint is inherently satisfied as the variable `NumberOfRegularCoffees` is defined with type CONTINUOUS, which is non-negative by default.

# Set objective
model.setObjective(TimePerMocha * NumberOfMochas + TimePerRegular * NumberOfRegularCoffees, gp.GRB.MINIMIZE)

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
