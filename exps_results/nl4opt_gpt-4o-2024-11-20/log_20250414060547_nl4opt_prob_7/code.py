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
WiredHeadphones = model.addVar(vtype=gp.GRB.INTEGER, name="WiredHeadphones")
WirelessHeadphones = model.addVar(vtype=gp.GRB.INTEGER, name="WirelessHeadphones")

# The integrality of "WiredHeadphones" is already enforced as it is declared as an integer variable. No additional constraint is needed.

# No code is needed as the integer nature of the WirelessHeadphones variable is already established during its definition.

# WiredHeadphones is already declared non-negative due to its default lower bound (0) in Gurobi.
# No additional code is needed for this constraint.

# The non-negativity constraint is inherently satisfied as variables in Gurobi default to a lower bound of 0 unless explicitly set otherwise.

# Add constraint for maximum wired headphones production
model.addConstr(WiredHeadphones <= MaxWired, name="max_wired_headphones")

# Add constraint to limit the number of wireless headphones produced per day
model.addConstr(WirelessHeadphones <= MaxWireless, name="MaxWirelessConstraint")

# Add constraint to ensure total usage of the audio testing machine is within its daily capacity
model.addConstr(WiredHeadphones + WirelessHeadphones <= MaxTesting, name="testing_capacity")

# Add constraint for limiting wired headphone production
model.addConstr(WiredHeadphones <= MaxWired, name="wired_headphone_limit")

# Add constraint to ensure wireless headphone production does not exceed maximum limit
model.addConstr(WirelessHeadphones <= MaxWireless, name="max_wireless_constraint")

# Add testing capacity constraint
model.addConstr(WiredHeadphones + WirelessHeadphones <= MaxTesting, name="testing_capacity")

# No additional code is needed as the non-negativity and integrality of WiredHeadphones are already captured by its definition.

# The non-negativity and integrality of the WirelessHeadphones variable is already defined in its creation (`vtype=gp.GRB.INTEGER` and no negative values allowed by default).

# Set objective
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
