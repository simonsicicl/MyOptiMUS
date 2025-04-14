import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_13/data.json", "r") as f:
    data = json.load(f)

B = data["B"] # scalar parameter
Cr = data["Cr"] # scalar parameter
Cs = data["Cs"] # scalar parameter
Er = data["Er"] # scalar parameter
Es = data["Es"] # scalar parameter
MinR = data["MinR"] # scalar parameter
MaxR = data["MaxR"] # scalar parameter
MinS = data["MinS"] # scalar parameter
NumberOfRadioAds = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfRadioAds")
NumberOfSocialMediaAds = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSocialMediaAds")

# Add constraint for the total cost of ads not exceeding the budget B
model.addConstr((Cr * NumberOfRadioAds) + (Cs * NumberOfSocialMediaAds) <= B, "budget_constraint")

# Add constraint to ensure the minimum number of radio ads is ordered
model.addConstr(NumberOfRadioAds >= MinR, name="min_radio_ads")

# Constraint: No more than MaxR radio ads should be ordered
model.addConstr(NumberOfRadioAds <= MaxR, name="max_radio_ads")

# Ensure at least MinS social media ads are contracted
model.addConstr(NumberOfSocialMediaAds >= MinS, name="min_social_media_ads")

# Define the objective function
model.setObjective(NumberOfRadioAds * Er + NumberOfSocialMediaAds * Es, gp.GRB.MAXIMIZE)

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
