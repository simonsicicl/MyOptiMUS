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
WaterSoftenerUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="WaterSoftenerUnits")
MaxTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MaxTime")

# Add non-negativity constraints for ChlorineUnits and WaterSoftenerUnits
model.addConstr(ChlorineUnits >= 0, name="non_negativity_ChlorineUnits")
model.addConstr(WaterSoftenerUnits >= 0, name="non_negativity_WaterSoftenerUnits")

# Add chlorine to water softener ratio constraint
model.addConstr(ChlorineUnits <= ChlorineSoftenerRatio * WaterSoftenerUnits, name="chlorine_softener_ratio")

# Add chlorine safety constraint  
model.addConstr(ChlorineUnits >= MinChlorine, name="chlorine_safety_requirement")

# Add constraint to ensure the total chemical units added equals TotalChemicals
model.addConstr(ChlorineUnits + WaterSoftenerUnits == TotalChemicals, name="total_chemicals_constraint")

# Add chlorine minimum requirement constraint
model.addConstr(ChlorineUnits >= MinChlorine, name="chlorine_minimum_requirement")

# Add total chemicals constraint
model.addConstr(ChlorineUnits + WaterSoftenerUnits == TotalChemicals, name="total_chemicals_constraint")

# Non-negativity constraint for chlorine units
model.addConstr(ChlorineUnits >= 0, name="non_negativity_chlorine_units")

# Non-negativity is inherently ensured by the default lower bound of 0 in gurobipy variables.

# Ensure that the number of ChlorineUnits satisfies the minimum chlorine requirement
model.addConstr(ChlorineUnits >= MinChlorine, name="min_chlorine_req")

# Add chlorine-to-water softener ratio constraint
model.addConstr(ChlorineUnits <= ChlorineSoftenerRatio * WaterSoftenerUnits, name="chlorine_softener_ratio")

# Add constraint to ensure MaxTime is greater than or equal to the chlorine readiness time
model.addConstr(MaxTime >= ChlorineTime * ChlorineUnits, name="chlorine_max_time_constraint")

# Add constraint to ensure MaxTime is greater than or equal to the water softener readiness time
model.addConstr(MaxTime >= WaterSoftenerTime * WaterSoftenerUnits, name="max_time_constraint")

# Enforce the minimum quantity of chlorine required
model.addConstr(ChlorineUnits >= MinChlorine, name="min_chlorine_constraint")

# Add constraint to enforce the maximum ratio of chlorine to water softener
model.addConstr(ChlorineUnits <= ChlorineSoftenerRatio * WaterSoftenerUnits, name="chlorine_softener_ratio")

# Add constraint to ensure the total amount of chemicals equals the required total
model.addConstr(ChlorineUnits + WaterSoftenerUnits == TotalChemicals, name="total_chemicals")

# Set objective
model.setObjective(MaxTime, gp.GRB.MINIMIZE)

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
