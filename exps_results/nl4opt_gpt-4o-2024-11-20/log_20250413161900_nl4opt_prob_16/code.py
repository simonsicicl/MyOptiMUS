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
NumberZtubeAds = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberZtubeAds")
NumberSoorchleAds = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberSoorchleAds")
NumberWassaAds = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberWassaAds")
TotalAds = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalAds")

# Change the variable type to integer as NumberZtubeAds must be non-negative and an integer
NumberZtubeAds.vtype = gp.GRB.INTEGER

# Changing the variable's integrality to enforce it being an integer
NumberSoorchleAds.vtype = gp.GRB.INTEGER

# Change integrality of the variable to ensure NumberWassaAds is an integer
NumberWassaAds.vtype = gp.GRB.INTEGER

# The constraint is already satisfied as the variable NumberZtubeAds is defined with a lower bound of 0 by default in gurobipy.

# Since the variable "NumberSoorchleAds" is already defined with non-negativity enforced as it is continuous, no constraint code is needed.

# Add constraint to ensure the number of advertisements placed on Wassa is non-negative
model.addConstr(NumberWassaAds >= 0, name="non_negative_wassa_ads")

# Add constraint to ensure total spending on z-tube advertisements doesn't exceed the budget
model.addConstr(NumberZtubeAds * CostZtube <= Budget, name="ztube_ad_budget")

# Add constraint to ensure total spending on Soorchle ads does not exceed the advertising budget
model.addConstr(NumberSoorchleAds * CostSoorchle <= Budget, name="Soorchle_ad_spending_constraint")

# Add constraint to ensure spending on Wassa advertisements does not exceed the budget
model.addConstr(NumberWassaAds * CostWassa <= Budget, name="Wassa_advertising_budget")

# Add budget constraint for advertisement spending
model.addConstr(
    NumberZtubeAds * CostZtube 
    + NumberSoorchleAds * CostSoorchle 
    + NumberWassaAds * CostWassa 
    <= Budget,
    name="AdSpendingBudget"
)

# Add constraint to limit the number of Soorchle ads
model.addConstr(NumberSoorchleAds <= MaxAdsSoorchle, name="max_soorchle_ads")

# Add constraint to restrict the number of Wassa ads
model.addConstr(
    NumberWassaAds <= (MaxPropWassa / (1 - MaxPropWassa)) * (NumberZtubeAds + NumberSoorchleAds), 
    name="WassaAdsLimit"
)

# Add constraint to ensure the number of z-tube ads is at least MinPropZtube times the total number of ads
model.addConstr((1 - MinPropZtube) * NumberZtubeAds - MinPropZtube * NumberSoorchleAds - MinPropZtube * NumberWassaAds >= 0, name="z_tube_min_ad_proportion")

# Add constraint for total advertising cost not exceeding the budget
model.addConstr(
    NumberZtubeAds * CostZtube + 
    NumberSoorchleAds * CostSoorchle + 
    NumberWassaAds * CostWassa <= Budget, 
    name="advertising_budget_constraint"
)

# Add constraint to ensure the number of advertisements on Soorchle does not exceed the maximum limit
model.addConstr(NumberSoorchleAds <= MaxAdsSoorchle, name="max_soorchle_ads")

# Add constraint to ensure the proportion of advertisements on Wassa does not exceed the maximum allowed proportion
model.addConstr(NumberWassaAds <= MaxPropWassa * TotalAds, name="max_proportion_wassa_ads")

# Add minimum proportion constraint for advertisements on z-tube
model.addConstr(NumberZtubeAds >= MinPropZtube * TotalAds, name="min_proportion_ztube_ads")

# Add constraint: Total number of advertisements is the sum of advertisements across all platforms
model.addConstr(TotalAds == NumberZtubeAds + NumberSoorchleAds + NumberWassaAds, name="total_ads_constraint")

# Set objective
model.setObjective(
    ViewersZtube * NumberZtubeAds +
    ViewersSoorchle * NumberSoorchleAds +
    ViewersWassa * NumberWassaAds,
    gp.GRB.MAXIMIZE
)

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
