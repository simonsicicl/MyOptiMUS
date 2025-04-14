import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_260/data.json", "r") as f:
    data = json.load(f)

FabricA = data["FabricA"] # scalar parameter
FabricB = data["FabricB"] # scalar parameter
PlasticA = data["PlasticA"] # scalar parameter
PlasticB = data["PlasticB"] # scalar parameter
ElementA = data["ElementA"] # scalar parameter
ElementB = data["ElementB"] # scalar parameter
TotalElement = data["TotalElement"] # scalar parameter
MinFabric = data["MinFabric"] # scalar parameter
MinPlastic = data["MinPlastic"] # scalar parameter
HoursA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursA")
HoursB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursB")

# At least MinFabric units of fabric must be produced using methods A and B
model.addConstr(FabricA * HoursA + FabricB * HoursB >= MinFabric, name="min_fabric_production")

# Add constraint to ensure at least MinPlastic units of plastic are produced
model.addConstr(PlasticA * HoursA + PlasticB * HoursB >= MinPlastic, name="min_plastic_produced")

model.addConstr(HoursA >= 0, name="non_negative_hours_A")

# Add constraint to ensure the number of hours using method B is non-negative
model.addConstr(HoursB >= 0, name="hoursB_non_negative")

# Ensure at least MinFabric units of fabric are produced
model.addConstr(FabricA * HoursA + FabricB * HoursB >= MinFabric, name="MinFabric_Production")

# Constraint to ensure at least MinPlastic units of plastic are produced
model.addConstr(PlasticA * HoursA + PlasticB * HoursB >= MinPlastic, name="min_plastic_produced")

# Constraint: Do not exceed the total available units of the special element
model.addConstr(ElementA * HoursA + ElementB * HoursB <= TotalElement, name="special_element_limit")

# Set objective
model.setObjective(HoursA + HoursB, gp.GRB.MINIMIZE)

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
