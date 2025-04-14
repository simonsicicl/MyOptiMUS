import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_95/data.json", "r") as f:
    data = json.load(f)

A = data["A"] # scalar parameter
HeapProduction = data["HeapProduction"] # scalar parameter
HeapWaste = data["HeapWaste"] # scalar parameter
HeapMachines = data["HeapMachines"] # scalar parameter
VatProduction = data["VatProduction"] # scalar parameter
VatWaste = data["VatWaste"] # scalar parameter
VatMachines = data["VatMachines"] # scalar parameter
MachinesAvailable = data["MachinesAvailable"] # scalar parameter
WasteLimit = data["WasteLimit"] # scalar parameter
HeapLeachingLand = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HeapLeachingLand")
VatLeachingLand = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VatLeachingLand")

# Constrain the total land used for heap leaching and vat leaching to not exceed A square miles
model.addConstr(HeapLeachingLand + VatLeachingLand <= A, name="land_usage_leaching_techniques")

# Constraint: Total number of machines used for heap leaching and vat leaching must not exceed the number of machines available
model.addConstr(HeapLeachingLand * HeapMachines + VatLeachingLand * VatMachines <= MachinesAvailable, "machines_usage_constraint")

# Add wastewater production constraint
wasteConstraint = HeapWaste * HeapLeachingLand + VatWaste * VatLeachingLand <= WasteLimit
model.addConstr(wasteConstraint, name="daily_waste_limit")

# Constraint: The area allocated to heap leaching is non-negative
model.addConstr(HeapLeachingLand >= 0, name="non_negative_heap_leaching_land")

# Ensure the area allocated to vat leaching is non-negative
model.addConstr(VatLeachingLand >= 0, name="VatLeachingLand_non_negative")

# Ensure the total land allocated for both techniques does not exceed the total area of mining sites
model.addConstr(HeapLeachingLand + VatLeachingLand <= A, name="total_land_constraint")

# Add machine usage constraint
model.addConstr(HeapLeachingLand * HeapMachines + VatLeachingLand * VatMachines <= MachinesAvailable, name="total_machine_usage")

# Add environmental regulation constraint for daily production of polluted wastewater
model.addConstr(HeapLeachingLand * HeapWaste + VatLeachingLand * VatWaste <= WasteLimit, name="env_regulations_waste_limit")

# Set objective
model.setObjective(HeapLeachingLand * HeapProduction + VatLeachingLand * VatProduction, gp.GRB.MAXIMIZE)

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
