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
NumRadioAds = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumRadioAds")
NumSocialAds = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumSocialAds")

# Add advertising budget constraint
model.addConstr(Cr * NumRadioAds + Cs * NumSocialAds <= B, name="advertising_budget")

# Add constraint to ensure the number of radio ads purchased is at least the minimum required
model.addConstr(NumRadioAds >= MinR, name="num_radio_ads_minimum")

# Add constraint on the number of radio ads
model.addConstr(NumRadioAds <= MaxR, name="max_radio_ads")

# Ensure at least MinS social media ads are contracted
model.addConstr(NumSocialAds >= MinS, name="min_social_ads")

# Add constraint for minimum and maximum number of radio ads
model.addConstr(NumRadioAds >= MinR, name="min_radio_ads")
model.addConstr(NumRadioAds <= MaxR, name="max_radio_ads")

# Add minimum number of social media ads constraint
model.addConstr(NumSocialAds >= MinS, name="min_social_ads")

# Add total cost constraint for ads within the budget
model.addConstr(Cr * NumRadioAds + Cs * NumSocialAds <= B, name="ads_budget_constraint")

# Add constraints to enforce the minimum and maximum limits on the number of radio ads
model.addConstr(NumRadioAds >= MinR, name="min_radio_ads")
model.addConstr(NumRadioAds <= MaxR, name="max_radio_ads")

# Add minimum number of social media ads constraint
model.addConstr(NumSocialAds >= MinS, name="min_social_ads")

# Set objective
model.setObjective(Er * NumRadioAds + Es * NumSocialAds, gp.GRB.MAXIMIZE)

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
