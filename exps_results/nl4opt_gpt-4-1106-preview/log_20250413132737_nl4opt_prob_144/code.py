import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_144/data.json", "r") as f:
    data = json.load(f)

ChlorineTime = data["ChlorineTime"] # scalar parameter
WaterSoftenerTime = data["WaterSoftenerTime"] # scalar parameter
MinChlorine = data["MinChlorine"] # scalar parameter
ChlorineSoftenerRatio = data["ChlorineSoftenerRatio"] # scalar parameter
TotalChemicals = data["TotalChemicals"] # scalar parameter
ChlorineUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ChlorineUnits")
WaterSoftenerUnits = model.addVar(vtype=gp.GRB.INTEGER, name="WaterSoftenerUnits")

# The variables are already ensured to be non-negative by default through their definitions with addVar
# No further constraint code is needed for non-negativity

# The amount of chlorine cannot exceed ChlorineSoftenerRatio times the amount of water softener
model.addConstr(ChlorineUnits <= ChlorineSoftenerRatio * WaterSoftenerUnits, name="chlorine_softener_ratio_constraint")

model.addConstr(ChlorineUnits >= MinChlorine, name="min_chlorine_requirement")

ChlorineUnits.vtype = gp.GRB.CONTINUOUS  # Ensure ChlorineUnits is continuous

model.addConstr(ChlorineUnits + WaterSoftenerUnits == TotalChemicals, name="Total_Chemicals_Constraint")

# Ensure that the minimum amount of chlorine is used
model.addConstr(ChlorineUnits >= MinChlorine, name="min_chlorine_requirement")

# Ensure that the ratio of chlorine to water softener does not exceed the maximum allowed
model.addConstr(ChlorineUnits <= ChlorineSoftenerRatio * WaterSoftenerUnits, name="chlorine_to_softener_ratio_constraint")

# Ensure that the total chemical units used in the pool meets the requirement.
model.addConstr(ChlorineUnits + WaterSoftenerUnits == TotalChemicals, name="total_chemicals_requirement")

# Define objective function
model.setObjective(ChlorineUnits * ChlorineTime + WaterSoftenerUnits * WaterSoftenerTime, gp.GRB.MINIMIZE)

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
