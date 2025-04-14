import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_284/data.json", "r") as f:
    data = json.load(f)

A = data["A"] # scalar parameter
TimeHeavyDuty = data["TimeHeavyDuty"] # scalar parameter
TimeGasMower = data["TimeGasMower"] # scalar parameter
PollutionHeavyDuty = data["PollutionHeavyDuty"] # scalar parameter
FuelHeavyDuty = data["FuelHeavyDuty"] # scalar parameter
PollutionGasMower = data["PollutionGasMower"] # scalar parameter
FuelGasMower = data["FuelGasMower"] # scalar parameter
FuelTotal = data["FuelTotal"] # scalar parameter
PollutionMax = data["PollutionMax"] # scalar parameter
SquareFeetHeavyDuty = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SquareFeetHeavyDuty")
SquareFeetGasMower = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SquareFeetGasMower")

# Add non-negativity constraint for SquareFeetHeavyDuty
model.addConstr(SquareFeetHeavyDuty >= 0, name="non_negativity_HeavyDuty")

# Add non-negativity constraint for SquareFeetGasMower
model.addConstr(SquareFeetGasMower >= 0, name="non_negative_SquareFeetGasMower")

# Add constraint ensuring the total square footage of grass cut equals the total area A
model.addConstr(SquareFeetHeavyDuty + SquareFeetGasMower == A, name="total_grass_cut_area")

# Add pollution constraint
model.addConstr(
    PollutionHeavyDuty * SquareFeetHeavyDuty + PollutionGasMower * SquareFeetGasMower <= PollutionMax, 
    name="pollution_constraint"
)

# Add constraint for total fuel usage
model.addConstr(
    SquareFeetHeavyDuty * FuelHeavyDuty + SquareFeetGasMower * FuelGasMower <= FuelTotal,
    name="total_fuel_constraint"
)

# Add constraint for total grass cut area 
model.addConstr(SquareFeetHeavyDuty + SquareFeetGasMower == A, name="total_grass_cut_constraint")

# Add constraint to ensure total fuel consumption does not exceed FuelTotal
model.addConstr(
    FuelHeavyDuty * SquareFeetHeavyDuty + FuelGasMower * SquareFeetGasMower <= FuelTotal, 
    name="total_fuel_limit"
)

# Add pollution constraint
model.addConstr(PollutionHeavyDuty * SquareFeetHeavyDuty + PollutionGasMower * SquareFeetGasMower <= PollutionMax, name="pollution_constraint")

# Set objective
model.setObjective(
    TimeHeavyDuty * SquareFeetHeavyDuty + TimeGasMower * SquareFeetGasMower,
    gp.GRB.MINIMIZE
)

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
