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

# Add fabric production constraint
model.addConstr(FabricA * HoursA + FabricB * HoursB >= MinFabric, name="fabric_production")

# Add constraint to meet or exceed the minimum required plastic production
model.addConstr(PlasticA * HoursA + PlasticB * HoursB >= MinPlastic, name="min_plastic_production")

# No additional code is required because the variable "HoursA" is already declared non-negative as its default lower bound in gurobipy is 0.

# No additional code needed since non-negativity is inherently ensured by the variable's default lower bound (0) in Gurobi.

# Add constraint to ensure total fabric production meets or exceeds the minimum required
model.addConstr(HoursA * FabricA + HoursB * FabricB >= MinFabric, name="fabric_production_requirement")

# Add constraint to ensure total plastic production meets or exceeds the minimum required
model.addConstr(HoursA * PlasticA + HoursB * PlasticB >= MinPlastic, name="min_plastic_production")

# Add constraint to ensure total consumption of the special element does not exceed availability
model.addConstr(HoursA * ElementA + HoursB * ElementB <= TotalElement, name="special_element_availability")

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
