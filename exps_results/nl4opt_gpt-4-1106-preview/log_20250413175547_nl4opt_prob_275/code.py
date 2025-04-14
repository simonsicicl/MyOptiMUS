import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_275/data.json", "r") as f:
    data = json.load(f)

TimeA = data["TimeA"] # scalar parameter
TimeB = data["TimeB"] # scalar parameter
MaxRatioAtoB = data["MaxRatioAtoB"] # scalar parameter
MinUnitsA = data["MinUnitsA"] # scalar parameter
MinTotalUnits = data["MinTotalUnits"] # scalar parameter
ChemicalAUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ChemicalAUnits")
ChemicalBUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ChemicalBUnits")

model.addConstr(ChemicalAUnits >= 0, name="non_negativity_ChemicalAUnits")

# Non-negativity constraint for ChemicalBUnits
model.addConstr(ChemicalBUnits >= 0, name="ChemicalBUnits_non_negative")

# Add constraint that for every unit of chemical B, there can be at most MaxRatioAtoB units of chemical A
model.addConstr(ChemicalAUnits <= MaxRatioAtoB * ChemicalBUnits, name="max_ratio_A_to_B")

# Ensure the mix contains at least the minimum required units of Chemical A
model.addConstr(ChemicalAUnits >= MinUnitsA, name="min_units_chemical_A")

# Constraint for minimum required units of Chemical A and B
model.addConstr(ChemicalAUnits + ChemicalBUnits >= MinTotalUnits, name="min_total_units")

# Ensure the ratio of chemical A to chemical B does not exceed the maximum allowed ratio
model.addConstr(ChemicalAUnits <= MaxRatioAtoB * ChemicalBUnits, name="Max_ChemicalA_to_ChemicalB_Ratio")

# Ensure at least the minimum required units of chemical A are used
model.addConstr(ChemicalAUnits >= MinUnitsA, name="min_chemical_A_units")

# Ensure the total units of chemicals meets the minimum requirement
model.addConstr(ChemicalAUnits + ChemicalBUnits >= MinTotalUnits, name="min_total_units")

# Set objective
model.setObjective(TimeA * ChemicalAUnits + TimeB * ChemicalBUnits, gp.GRB.MINIMIZE)

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
