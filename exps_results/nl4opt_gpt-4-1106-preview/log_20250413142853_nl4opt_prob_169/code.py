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
Camels = model.addVar(vtype=gp.GRB.INTEGER, name="Camels")
Horses = model.addVar(vtype=gp.GRB.INTEGER, name="Horses")

# The number of camels must be a non-negative integer constraint is inherently satisfied
# by the variable definition using vtype=gp.GRB.INTEGER and Gurobi's default lower bound of 0.

# Add non-negativity constraint for the number of horses
model.addConstr(Horses >= 0, name="non_negativity_horses")

# Add minimum package delivery constraint
model.addConstr(Camels * CamelCapacity + Horses * HorseCapacity >= MinPackages, name="min_packages_delivery")

# Add constraint for the total food consumed by camels and horses
model.addConstr(Camels * CamelFood + Horses * HorseFood <= TotalFood, name="Total_Food_Consumption")

model.addConstr(Horses <= Camels, name="horses_leq_camels")

# Ensure total carrying capacity of camels and horses meets minimum packages
model.addConstr(Camels * CamelCapacity + Horses * HorseCapacity >= MinPackages, "min_delivery_capacity")

# Ensure that the total food consumed by camels and horses does not exceed the total food available
model.addConstr(Camels * CamelFood + Horses * HorseFood <= TotalFood, name="food_consumption")

# Set objective
model.setObjective(Camels + Horses, gp.GRB.MINIMIZE)

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
