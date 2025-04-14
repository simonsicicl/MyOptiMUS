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
LoavesBread = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LoavesBread")
BatchesCookies = model.addVar(vtype=gp.GRB.INTEGER, name="BatchesCookies")

# Total mixer hours constraint for bread and cookies not exceeding MaxHours
model.addConstr(LoavesBread * BreadMixerHours + BatchesCookies * CookieMixerHours <= MaxHours, "MixerHoursConstraint")

LoavesBread = model.addVar(vtype=gp.GRB.CONTINUOUS, name='LoavesBread')
BatchesCookies = model.addVar(vtype=gp.GRB.INTEGER, name='BatchesCookies')

# The number of loaves of bread produced must be non-negative
model.addConstr(LoavesBread >= 0, name="non_negative_loaves")

# Add non-negativity constraint for the number of batches of cookies
model.addConstr(BatchesCookies >= 0, name="non_negativity_batches")

# Mixer operational hours constraint
model.addConstr(BreadMixerHours * LoavesBread + CookieMixerHours * BatchesCookies <= MaxHours, name="mixer_operational_hours")

# Add constraint for the oven usage within available operational hours
model.addConstr(BreadOvenHours * LoavesBread + CookieOvenHours * BatchesCookies <= MaxHours, name="OvenOperationalHours")

# Set objective
model.setObjective(ProfitBread * LoavesBread + ProfitCookies * BatchesCookies, gp.GRB.MAXIMIZE)

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
