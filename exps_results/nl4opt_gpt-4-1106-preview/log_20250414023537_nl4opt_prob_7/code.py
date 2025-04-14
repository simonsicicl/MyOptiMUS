import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_7/data.json", "r") as f:
    data = json.load(f)

MaxWired = data["MaxWired"] # scalar parameter
MaxWireless = data["MaxWireless"] # scalar parameter
MaxTesting = data["MaxTesting"] # scalar parameter
ProfitWired = data["ProfitWired"] # scalar parameter
ProfitWireless = data["ProfitWireless"] # scalar parameter
WiredHeadphones = model.addVar(vtype=gp.GRB.CONTINUOUS, name="WiredHeadphones")
WirelessHeadphones = model.addVar(vtype=gp.GRB.CONTINUOUS, name="WirelessHeadphones")

WiredHeadphones.VType = gp.GRB.INTEGER

WirelessHeadphones.vtype = gp.GRB.INTEGER

# Constraint: Number of wired headphones produced must be non-negative
model.addConstr(WiredHeadphones >= 0, name="non_negative_production")

# Constraint: Number of wireless headphones produced must be non-negative
model.addConstr(WirelessHeadphones >= 0, name="non_negative_production")

# Add constraint for the maximum production capacity of wired headphones
model.addConstr(WiredHeadphones <= MaxWired, name="max_wired_capacity")

# Add constraint for the maximum daily production capacity of the wireless team
model.addConstr(WirelessHeadphones <= MaxWireless, "max_daily_wireless_capacity")

# Add the constraint for the testing machine's capacity
model.addConstr(WiredHeadphones + WirelessHeadphones <= MaxTesting, name="TestingMachineCapacity")

# Define the objective function
model.setObjective(ProfitWired * WiredHeadphones + ProfitWireless * WirelessHeadphones, gp.GRB.MAXIMIZE)

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
