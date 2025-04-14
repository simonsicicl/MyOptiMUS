import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_21/data.json", "r") as f:
    data = json.load(f)

MaxHours = data["MaxHours"] # scalar parameter
BreadMixerHours = data["BreadMixerHours"] # scalar parameter
BreadOvenHours = data["BreadOvenHours"] # scalar parameter
CookieMixerHours = data["CookieMixerHours"] # scalar parameter
CookieOvenHours = data["CookieOvenHours"] # scalar parameter
ProfitBread = data["ProfitBread"] # scalar parameter
ProfitCookies = data["ProfitCookies"] # scalar parameter
BreadProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BreadProduced")
CookiesProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CookiesProduced")

# Add constraint for maximum operational hours for the stand mixer
model.addConstr(
    BreadProduced * BreadMixerHours + CookiesProduced * CookieMixerHours <= MaxHours,
    name="mixer_hours_limit"
)

# Add constraint for total oven hours not exceeding maximum operational hours
model.addConstr(
    BreadProduced * BreadOvenHours + CookiesProduced * CookieOvenHours <= MaxHours,
    name="total_oven_hours_constraint"
)

# The non-negativity of the output is already enforced by the variable bounds set during its definition (lower bound defaults to 0 in Gurobi).

# Non-negativity constraint for CookiesProduced
model.addConstr(CookiesProduced >= 0, name="non_negativity_CookiesProduced")

# Add constraint to ensure total stand-mixer usage hours do not exceed MaxHours
model.addConstr(BreadMixerHours * BreadProduced + CookieMixerHours * CookiesProduced <= MaxHours, name="mixer_usage_limit")

# Add constraint for total oven usage hours
model.addConstr(
    BreadOvenHours * BreadProduced + CookieOvenHours * CookiesProduced <= MaxHours,
    name="total_oven_usage"
)

# Set objective
model.setObjective(ProfitBread * BreadProduced + ProfitCookies * CookiesProduced, gp.GRB.MAXIMIZE)

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
