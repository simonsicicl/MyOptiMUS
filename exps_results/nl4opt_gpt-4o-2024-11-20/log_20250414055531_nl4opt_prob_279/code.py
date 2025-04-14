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
MatchaIceCreamOrders = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MatchaIceCreamOrders")
OrangeSorbetOrders = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OrangeSorbetOrders")

# The variable MatchaIceCreamOrders is already constrained to non-negative domain by default as it is declared as continuous (vtype=gp.GRB.CONTINUOUS).

# Non-negativity of OrangeSorbetOrders is implicitly ensured by the default lower bound of 0 in gurobipy variables.

# Add constraint ensuring at least MinProportionMatcha of desserts made must be matcha ice cream
model.addConstr((1 - MinProportionMatcha) * MatchaIceCreamOrders >= MinProportionMatcha * OrangeSorbetOrders, name="min_proportion_matcha")

# Adding constraint to ensure total ice cream used does not exceed available ice cream
model.addConstr(MatchaIceCreamOrders * IceCreamMatcha <= TotalIceCream, name="ice_cream_constraint")

# Add constraint to ensure total water used does not exceed available water
model.addConstr(OrangeSorbetOrders * WaterOrange <= TotalWater, name="water_usage_constraint")

# Add constraint to enforce the minimum proportion of matcha ice cream orders
model.addConstr((1 - MinProportionMatcha) * MatchaIceCreamOrders >= MinProportionMatcha * OrangeSorbetOrders, name="min_proportion_matcha")

# Set objective
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
