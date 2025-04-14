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
LowPowerAirConditioners = model.addVar(vtype=gp.GRB.INTEGER, name="LowPowerAirConditioners")
HighPowerAirConditioners = model.addVar(vtype=gp.GRB.INTEGER, name="HighPowerAirConditioners")

# Since LowPowerAirConditioners is an INTEGER variable in Gurobi and Gurobi doesn't allow negative integers by definition, 
# there's no need to add an explicit non-negative constraint.
# Hence, no code is needed for this constraint.

# In case the variable was not limited to non-negative values, the constraint would be as follows:
# model.addConstr(LowPowerAirConditioners >= 0, name="low_power_ac_nonnegativity")

# Since the variable HighPowerAirConditioners is already non-negative by definition,
# and it is an integer variable, no further constraint is needed.

# Limit the number of low-power air conditioners to MaxLowPowerProportion of the total air conditioners
model.addConstr(LowPowerAirConditioners <= MaxLowPowerProportion * (LowPowerAirConditioners + HighPowerAirConditioners), "LowPowerAirConditioners_limit")

# Constraint for the minimum number of high-powered air conditioners
model.addConstr(HighPowerAirConditioners >= MinHighPower, name="min_high_power_acs")

# Ensure that the total number of housing units conditioned by the air conditioners is at least the minimum required
model.addConstr(LowPowerCapacity * LowPowerAirConditioners + HighPowerCapacity * HighPowerAirConditioners >= MinHousingUnits, name="min_housing_units_conditioned")

# Add constraint for total electricity usage by air conditioners not to exceed available electricity
model.addConstr(LowPowerElectricity * LowPowerAirConditioners + HighPowerElectricity * HighPowerAirConditioners <= TotalElectricity, name="electricity_usage")

# Ensure that no more than the maximum proportion of air conditioners are low-powered models
model.addConstr(LowPowerAirConditioners <= MaxLowPowerProportion * (LowPowerAirConditioners + HighPowerAirConditioners), name="max_low_power_proportion")

# Ensure that there are at least the minimum number of high-powered air conditioners
model.addConstr(HighPowerAirConditioners >= MinHighPower, name="min_high_power_ac_constraint")

# Ensure the cooling capacity meets the minimum requirement for housing units
model.addConstr(LowPowerCapacity * LowPowerAirConditioners + HighPowerCapacity * HighPowerAirConditioners >= MinHousingUnits, name="min_cooling_capacity")

# Ensure the total electricity usage does not exceed the total electricity available per day
model.addConstr(LowPowerElectricity * LowPowerAirConditioners + HighPowerElectricity * HighPowerAirConditioners <= TotalElectricity, "TotalElectricityUsage")

# Set objective
model.setObjective(LowPowerAirConditioners + HighPowerAirConditioners, gp.GRB.MINIMIZE)

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
