import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_169/data.json", "r") as f:
    data = json.load(f)

CamelCapacity = data["CamelCapacity"] # scalar parameter
HorseCapacity = data["HorseCapacity"] # scalar parameter
CamelFood = data["CamelFood"] # scalar parameter
HorseFood = data["HorseFood"] # scalar parameter
MinPackages = data["MinPackages"] # scalar parameter
TotalFood = data["TotalFood"] # scalar parameter
NumberOfCamels = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCamels")
NumberOfHorses = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfHorses")

# The variable "NumberOfCamels" is non-negative due to its default lower bound (0) in Gurobi's variable definition.

# The non-negativity constraint is inherently satisfied as the variable "NumberOfHorses" is defined as continuous (non-negative by default), no extra constraint needs to be added.

# Add a constraint ensuring the total delivered packages meet or exceed MinPackages
model.addConstr(NumberOfCamels * CamelCapacity + NumberOfHorses * HorseCapacity >= MinPackages, name="min_packages_constraint")

# Add constraint to ensure total food consumed does not exceed available food
model.addConstr(
    CamelFood * NumberOfCamels + HorseFood * NumberOfHorses <= TotalFood,
    name="food_constraint"
)

# Add constraint to ensure the number of horses does not exceed the number of camels
model.addConstr(NumberOfHorses <= NumberOfCamels, name="horses_cannot_exceed_camels")

# Add total delivery constraint for camels and horses
model.addConstr(CamelCapacity * NumberOfCamels + HorseCapacity * NumberOfHorses >= MinPackages, name="delivery_requirement")

# Add food consumption constraint for camels and horses
model.addConstr(
    NumberOfCamels * CamelFood + NumberOfHorses * HorseFood <= TotalFood,
    name="food_consumption"
)

# Add constraint to ensure the number of horses used is not greater than the number of camels
model.addConstr(NumberOfHorses <= NumberOfCamels, name="fewer_horses_than_camels")

# Set objective
model.setObjective(NumberOfCamels + NumberOfHorses, gp.GRB.MINIMIZE)

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
