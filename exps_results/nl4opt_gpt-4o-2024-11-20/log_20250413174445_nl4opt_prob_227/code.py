import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_227/data.json", "r") as f:
    data = json.load(f)

SubsoilWater = data["SubsoilWater"] # scalar parameter
TopsoilWater = data["TopsoilWater"] # scalar parameter
TotalBags = data["TotalBags"] # scalar parameter
MinTopsoil = data["MinTopsoil"] # scalar parameter
MaxTopsoilProportion = data["MaxTopsoilProportion"] # scalar parameter
SubsoilBags = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SubsoilBags")
TopsoilBags = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TopsoilBags")
TotalBagsUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalBagsUsed")

# Ensure the number of subsoil bags cannot be negative
model.addConstr(SubsoilBags >= 0, name="non_negative_subsoil_bags")

# Ensure the number of topsoil bags is non-negative
model.addConstr(TopsoilBags >= 0, name="non_negative_topsoil_bags")

# Add constraint for combined number of subsoil and topsoil bags not exceeding TotalBags
model.addConstr(SubsoilBags + TopsoilBags <= TotalBags, name="total_bags_limit")

# Add constraint to enforce the minimum required number of topsoil bags
model.addConstr(TopsoilBags >= MinTopsoil, name="min_topsoil_requirement")

# Add constraint to limit the number of topsoil bags
model.addConstr(TopsoilBags <= MaxTopsoilProportion * (TopsoilBags + SubsoilBags), name="topsoil_limit")

# Add constraint to ensure the sum of SubsoilBags and TopsoilBags does not exceed TotalBags
model.addConstr(SubsoilBags + TopsoilBags <= TotalBags, name="bag_limit_constraint")

# Add constraint to ensure the number of topsoil bags meets the minimum required
model.addConstr(TopsoilBags >= MinTopsoil, name="min_topsoil_constraint")

# Add constraint to ensure TopsoilBags do not exceed the maximum proportion of TotalBagsUsed
model.addConstr(TopsoilBags <= MaxTopsoilProportion * TotalBagsUsed, name="max_topsoil_proportion_constraint")

# Add constraint to define TotalBagsUsed as the sum of SubsoilBags and TopsoilBags
model.addConstr(TotalBagsUsed == SubsoilBags + TopsoilBags, name="total_bags_constraint")

# Set objective
model.setObjective(SubsoilWater * SubsoilBags + TopsoilWater * TopsoilBags, gp.GRB.MINIMIZE)

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
