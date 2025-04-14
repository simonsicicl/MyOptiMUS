import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_218/data.json", "r") as f:
    data = json.load(f)

ProfitRegular = data["ProfitRegular"] # scalar parameter
ProfitDeluxe = data["ProfitDeluxe"] # scalar parameter
DemandRegularMax = data["DemandRegularMax"] # scalar parameter
DemandDeluxeMax = data["DemandDeluxeMax"] # scalar parameter
SupplyTotalMax = data["SupplyTotalMax"] # scalar parameter
x1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="x1")
x2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="x2")

# Add non-negativity constraint for the quantity of regular tacos made
model.addConstr(x1 >= 0, name="x1_non_negativity")

model.addConstr(x2 >= 0, name="deluxe_taco_nonnegativity")

# Ensure the number of regular tacos does not exceed maximum demand
model.addConstr(x1 <= DemandRegularMax, name="regular_taco_demand_constraint")

model.addConstr(x2 <= DemandDeluxeMax, name="deluxe_taco_demand_constraint")

# Add constraint: Total number of tacos made must not exceed the supply limit
model.addConstr(x1 + x2 <= SupplyTotalMax, name="supply_limit")

# Set objective function
model.setObjective(ProfitRegular * x1 + ProfitDeluxe * x2, gp.GRB.MAXIMIZE)

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
