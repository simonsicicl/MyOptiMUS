import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_229/data.json", "r") as f:
    data = json.load(f)

LowPowerCapacity = data["LowPowerCapacity"] # scalar parameter
LowPowerElectricity = data["LowPowerElectricity"] # scalar parameter
HighPowerCapacity = data["HighPowerCapacity"] # scalar parameter
HighPowerElectricity = data["HighPowerElectricity"] # scalar parameter
MaxLowPowerProportion = data["MaxLowPowerProportion"] # scalar parameter
MinHighPower = data["MinHighPower"] # scalar parameter
MinHousingUnits = data["MinHousingUnits"] # scalar parameter
TotalElectricity = data["TotalElectricity"] # scalar parameter
LowPowerUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LowPowerUnits")
HighPowerUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HighPowerUnits")

# No additional code needed since LowPowerUnits is already defined as a non-negative continuous variable

# Non-negativity constraint for high-power air conditioners
model.addConstr(HighPowerUnits >= 0, name="non_negativity_HighPowerUnits")

# Add constraint to limit the number of low-power air conditioners relative to high-power air conditioners
model.addConstr(LowPowerUnits * (1 - MaxLowPowerProportion) <= MaxLowPowerProportion * HighPowerUnits, name="low_high_power_limit")

# Add constraint to enforce at least MinHighPower high-powered air conditioners are used
model.addConstr(HighPowerUnits >= MinHighPower, name="min_high_power_constraint")

# Add minimum housing units cooling constraint
model.addConstr(
    LowPowerUnits * LowPowerCapacity + HighPowerUnits * HighPowerCapacity >= MinHousingUnits,
    name="min_housing_units_cooling"
)

# Add constraint to limit total electricity usage
model.addConstr(
    LowPowerUnits * LowPowerElectricity + HighPowerUnits * HighPowerElectricity <= TotalElectricity,
    name="electricity_usage_limit"
)

# Add cooling capacity constraint
model.addConstr(
    LowPowerCapacity * LowPowerUnits + HighPowerCapacity * HighPowerUnits >= MinHousingUnits,
    name="cooling_capacity_constraint"
)

# Add electricity usage constraint
model.addConstr(
    LowPowerElectricity * LowPowerUnits + HighPowerElectricity * HighPowerUnits <= TotalElectricity,
    name="electricity_usage_constraint"
)

# Add constraint: Proportion of LowPowerUnits cannot exceed MaxLowPowerProportion
model.addConstr(
    LowPowerUnits <= MaxLowPowerProportion * (LowPowerUnits + HighPowerUnits),
    name="low_power_proportion"
)

# Add constraint to ensure at least the minimum number of high-power air conditioners are purchased
model.addConstr(HighPowerUnits >= MinHighPower, name="min_high_power_units")

# Set objective
model.setObjective(LowPowerUnits + HighPowerUnits, gp.GRB.MINIMIZE)

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
