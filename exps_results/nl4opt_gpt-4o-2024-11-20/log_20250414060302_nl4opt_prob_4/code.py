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
DeskLamps = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DeskLamps")
NightLamps = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NightLamps")

# Update the DeskLamps variable to be an integer type
DeskLamps.vtype = gp.GRB.INTEGER

# Change the variable type of NightLamps to integer
NightLamps.vtype = gp.GRB.INTEGER

# Non-negativity constraint for the number of desk-lamps
model.addConstr(DeskLamps >= 0, name="non_negativity_desk_lamps")

# Non-negativity constraint for the number of night-lamps
model.addConstr(NightLamps >= 0, name="non_negativity_nightlamps")

# Add constraint to ensure daily production of desk-lamps meets or exceeds minimum demand
model.addConstr(DeskLamps >= MinDesk, name="min_desk_lamps_demand")

# Ensure minimum daily production of night-lamps meets the demand
model.addConstr(NightLamps >= MinNight, name="min_night_lamps_constraint")

# Add constraint for maximum daily production of desk-lamps
model.addConstr(DeskLamps <= MaxDesk, name="max_daily_desk_lamps")

# Add constraint for maximum daily production of night-lamps
model.addConstr(NightLamps <= MaxNight, name="max_daily_nightlamp_production")

# Add constraint for total lamp production
model.addConstr(DeskLamps + NightLamps >= MinTotal, name="total_lamp_production")

# Set objective
model.setObjective(ProfitDesk * DeskLamps + ProfitNight * NightLamps, gp.GRB.MAXIMIZE)

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
