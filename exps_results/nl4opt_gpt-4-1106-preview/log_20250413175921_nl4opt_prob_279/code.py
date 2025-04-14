import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_279/data.json", "r") as f:
    data = json.load(f)

FlavouringMatcha = data["FlavouringMatcha"] # scalar parameter
IceCreamMatcha = data["IceCreamMatcha"] # scalar parameter
FlavouringOrange = data["FlavouringOrange"] # scalar parameter
WaterOrange = data["WaterOrange"] # scalar parameter
MinProportionMatcha = data["MinProportionMatcha"] # scalar parameter
TotalIceCream = data["TotalIceCream"] # scalar parameter
TotalWater = data["TotalWater"] # scalar parameter
MatchaIceCreamOrders = model.addVar(vtype=gp.GRB.INTEGER, name="MatchaIceCreamOrders")
OrangeSorbetOrders = model.addVar(vtype=gp.GRB.INTEGER, name="OrangeSorbetOrders")

model.addConstr(MatchaIceCreamOrders >= 0, name="matcha_orders_non_negative")

# Add constraint to ensure the number of orange sorbet orders is non-negative
model.addConstr(OrangeSorbetOrders >= 0, name="non_negative_orange_sorbet_orders")

# At least a certain proportion of total desserts made must be matcha ice cream
model.addConstr(MatchaIceCreamOrders >= MinProportionMatcha * (MatchaIceCreamOrders + OrangeSorbetOrders), name="min_proportion_matcha")

# Set objective function
model.setObjective(FlavouringMatcha * MatchaIceCreamOrders + FlavouringOrange * OrangeSorbetOrders, gp.GRB.MINIMIZE)

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
