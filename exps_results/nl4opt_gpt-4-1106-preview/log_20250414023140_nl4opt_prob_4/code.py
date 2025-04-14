import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_4/data.json", "r") as f:
    data = json.load(f)

MinDesk = data["MinDesk"] # scalar parameter
MinNight = data["MinNight"] # scalar parameter
MaxDesk = data["MaxDesk"] # scalar parameter
MaxNight = data["MaxNight"] # scalar parameter
MinTotal = data["MinTotal"] # scalar parameter
ProfitDesk = data["ProfitDesk"] # scalar parameter
ProfitNight = data["ProfitNight"] # scalar parameter
DeskLampsProducedPerDay = model.addVar(vtype=gp.GRB.INTEGER, name="DeskLampsProducedPerDay")
NightLampsProducedPerDay = model.addVar(vtype=gp.GRB.INTEGER, name="NightLampsProducedPerDay")

# No code needed since the variable DeskLampsProducedPerDay is already defined as INTEGER

# The number of night-lamps produced per day must be an integer value
# The constraint is already handled by the variable type definition.
# Hence, no additional constraint code is required.

# Since DeskLampsProducedPerDay is already an integer variable, we only need to add a constraint to ensure non-negativity.
model.addConstr(DeskLampsProducedPerDay >= 0, name="non_negative_desklamps")

# Constraint: The number of night-lamps produced per day must be non-negative
model.addConstr(NightLampsProducedPerDay >= 0, name="non_negative_night_lamps")

# Constraint for minimum daily production of desk-lamps
model.addConstr(DeskLampsProducedPerDay >= MinDesk, name="min_daily_desk_lamps")

# Add minimum production constraint for night-lamps
model.addConstr(NightLampsProducedPerDay >= MinNight, name="min_night_lamp_production")

# Add the maximum production constraint for desk-lamps per day
model.addConstr(DeskLampsProducedPerDay <= MaxDesk, name="max_desk_lamps_produced_per_day")

# Add the maximum production constraint for night-lamps per day
model.addConstr(NightLampsProducedPerDay <= MaxNight, name="max_night_lamps_produced_per_day")

# Add constraint for minimum total production of lamps per day
model.addConstr(DeskLampsProducedPerDay + NightLampsProducedPerDay >= MinTotal, "min_total_production")

# Add demand and production constraints for desk-lamps
model.addConstr(DeskLampsProducedPerDay >= MinDesk, name="min_desk_lamps_demand")
model.addConstr(DeskLampsProducedPerDay <= MaxDesk, name="max_desk_lamps_production")

# Add constraint for the production of night-lamps to be within the minimum demand and maximum production limits per day
model.addConstr(NightLampsProducedPerDay >= MinNight, name="min_night_lamps_demand")
model.addConstr(NightLampsProducedPerDay <= MaxNight, name="max_night_lamps_production")

# Constraint for minimum total production of lamps per day
model.addConstr(DeskLampsProducedPerDay + NightLampsProducedPerDay >= MinTotal, name="min_total_production")

# Define variables
DeskLampsProducedPerDay = model.addVar(vtype=gp.GRB.INTEGER, name="DeskLampsProducedPerDay")
NightLampsProducedPerDay = model.addVar(vtype=gp.GRB.INTEGER, name="NightLampsProducedPerDay")

# Define parameters
ProfitDesk = data["ProfitDesk"] # scalar parameter
ProfitNight = data["ProfitNight"] # scalar parameter

# Set objective
model.setObjective(ProfitDesk * DeskLampsProducedPerDay + ProfitNight * NightLampsProducedPerDay, gp.GRB.MAXIMIZE)

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
