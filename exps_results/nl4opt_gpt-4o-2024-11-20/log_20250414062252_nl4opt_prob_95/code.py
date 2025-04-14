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
HeapLand = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HeapLand")
VatLand = model.addVar(vtype=gp.GRB.CONTINUOUS, name="VatLand")

# Add constraint to ensure total land allocated does not exceed available area
model.addConstr(HeapLand + VatLand <= A, name="land_allocation_limit")

# Add machine usage constraint
model.addConstr(
    HeapMachines * HeapLand + VatMachines * VatLand <= MachinesAvailable,
    name="machine_usage"
)

# Adding the constraint to ensure total wastewater production does not exceed the daily waste limit
model.addConstr(HeapLand * HeapWaste + VatLand * VatWaste <= WasteLimit, name="wastewater_limit")

# Add non-negativity constraint for HeapLand
model.addConstr(HeapLand >= 0, name="HeapLand_nonnegativity")

# Add non-negativity constraint for VatLand
model.addConstr(VatLand >= 0, name="non_negativity_VatLand")

# Adding constraint: Heap leaching land allocation must be non-negative
model.addConstr(HeapLand >= 0, name="heap_land_nonnegativity")

# Vat leaching land allocation must be non-negative
model.addConstr(VatLand >= 0, name="vat_leaching_nonnegativity")

# Add constraint to ensure land allocation doesn't exceed available mining site area
model.addConstr(HeapLand + VatLand <= A, name="land_allocation_constraint")

# Add constraint to ensure the total machines allocated for heap and vat leaching does not exceed machines available
model.addConstr(HeapMachines * HeapLand + VatMachines * VatLand <= MachinesAvailable, name="machine_allocation")

# Add the total waste generation constraint
model.addConstr(HeapWaste * HeapLand + VatWaste * VatLand <= WasteLimit, name="total_waste_limit")

# Non-negativity constraint for HeapLand
model.addConstr(HeapLand >= 0, name="HeapLand_nonnegativity")

# No additional code is required because the variable "VatLand" is already declared non-negative as it's defined with the default lower bound of 0 in gurobipy.

# Set objective
model.setObjective(HeapProduction * HeapLand + VatProduction * VatLand, gp.GRB.MAXIMIZE)

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
