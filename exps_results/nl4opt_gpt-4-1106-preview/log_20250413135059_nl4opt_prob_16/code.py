import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_16/data.json", "r") as f:
    data = json.load(f)

CostZtube = data["CostZtube"] # scalar parameter
ViewersZtube = data["ViewersZtube"] # scalar parameter
CostSoorchle = data["CostSoorchle"] # scalar parameter
ViewersSoorchle = data["ViewersSoorchle"] # scalar parameter
CostWassa = data["CostWassa"] # scalar parameter
ViewersWassa = data["ViewersWassa"] # scalar parameter
MaxAdsSoorchle = data["MaxAdsSoorchle"] # scalar parameter
MaxPropWassa = data["MaxPropWassa"] # scalar parameter
MinPropZtube = data["MinPropZtube"] # scalar parameter
Budget = data["Budget"] # scalar parameter
NumZtubeAds = model.addVar(vtype=gp.GRB.INTEGER, name="NumZtubeAds")
NumSoorchleAds = model.addVar(vtype=gp.GRB.INTEGER, name="NumSoorchleAds")
NumWassaAds = model.addVar(vtype=gp.GRB.INTEGER, name="NumWassaAds")

# The variable NumZtubeAds is already defined as an integer, no additional constraint is needed.

# No code needed since the variable NumSoorchleAds is already defined as an integer in the given code snippet.

# Since NumWassaAds has already been defined as an integer variable, no additional constraint is required for integrality.

# The number of advertisements placed on z-tube must be non-negative
model.addConstr(NumZtubeAds >= 0, name="num_ztube_ads_non_negative")

# No code needed since the variable NumSoorchleAds is already guaranteed to be non-negative due to it being an integer variable in Gurobi.

# Add non-negativity constraint for the number of advertisements on wassa
model.addConstr(NumWassaAds >= 0, name="non_negativity_wassa_ads")

# Total spending on z-tube ads does not exceed Budget
model.addConstr(NumZtubeAds * CostZtube <= Budget, name="budget_constraint")

# Constraint: Total spending on soorchle ads does not exceed Budget
model.addConstr(NumSoorchleAds * CostSoorchle <= Budget, name="ad_spending_limit")

CostWassa = data["CostWassa"] # scalar parameter
Budget = data["Budget"] # scalar parameter
NumWassaAds = model.addVar(vtype=gp.GRB.INTEGER, name="NumWassaAds")

# Constraint: Total spending on wassa ads does not exceed Budget
model.addConstr(CostWassa * NumWassaAds <= Budget, name="spending_wassa_ads")

NumZtubeAds = model.addVar(vtype=gp.GRB.INTEGER, name='NumZtubeAds')
NumSoorchleAds = model.addVar(vtype=gp.GRB.INTEGER, name='NumSoorchleAds')
NumWassaAds = model.addVar(vtype=gp.GRB.INTEGER, name='NumWassaAds')

# Example: Add budget constraint
model.addConstr(CostZtube * NumZtubeAds + CostSoorchle * NumSoorchleAds + CostWassa * NumWassaAds <= Budget, 'BudgetConstraint')

# Example: Objective to maximize some function of the ad numbers (needs to be formulated according to the problem context)
model.setObjective(CostZtube * NumZtubeAds + CostSoorchle * NumSoorchleAds + CostWassa * NumWassaAds, gp.GRB.MAXIMIZE)

model.optimize()

# Add constraint for the maximum number of advertisements on soorchle
model.addConstr(NumSoorchleAds <= MaxAdsSoorchle, name="max_ads_soorchle")

# Add constraint for the maximum proportion of Wassa ads
model.addConstr(NumWassaAds <= MaxPropWassa * (NumZtubeAds + NumSoorchleAds + NumWassaAds), name="max_wassa_ads_prop")

# Add constraint for the minimum proportion of Z-tube advertisements
model.addConstr(NumZtubeAds >= MinPropZtube * (NumZtubeAds + NumSoorchleAds + NumWassaAds), name="min_prop_ztube")

# Define the objective function
objective = ViewersZtube * NumZtubeAds + ViewersSoorchle * NumSoorchleAds + ViewersWassa * NumWassaAds

# Set the objective in the model
model.setObjective(objective, gp.GRB.MAXIMIZE)

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
