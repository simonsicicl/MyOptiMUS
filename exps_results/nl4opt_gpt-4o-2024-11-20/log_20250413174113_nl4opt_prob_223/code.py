import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_223/data.json", "r") as f:
    data = json.load(f)

CostPiTV = data["CostPiTV"] # scalar parameter
ReachPiTV = data["ReachPiTV"] # scalar parameter
MaxCommercialsBetaVideo = data["MaxCommercialsBetaVideo"] # scalar parameter
CostBetaVideo = data["CostBetaVideo"] # scalar parameter
ReachBetaVideo = data["ReachBetaVideo"] # scalar parameter
CostGammaLive = data["CostGammaLive"] # scalar parameter
ReachGammaLive = data["ReachGammaLive"] # scalar parameter
MaxPropGammaLive = data["MaxPropGammaLive"] # scalar parameter
MinPropPiTV = data["MinPropPiTV"] # scalar parameter
WeeklyBudget = data["WeeklyBudget"] # scalar parameter
NumCommercialsPiTV = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumCommercialsPiTV")
NumCommercialsBetaVideo = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumCommercialsBetaVideo")
NumCommercialsGammaLive = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumCommercialsGammaLive")

# Add non-negativity constraints for the number of commercials
model.addConstr(NumCommercialsPiTV >= 0, name="NonNegativity_PiTV")
model.addConstr(NumCommercialsBetaVideo >= 0, name="NonNegativity_BetaVideo")
model.addConstr(NumCommercialsGammaLive >= 0, name="NonNegativity_GammaLive")

# Add constraint for maximum number of commercials allowed on Beta Video
model.addConstr(NumCommercialsBetaVideo <= MaxCommercialsBetaVideo, name="max_commercials_beta_video")

# Add constraint for the maximum number of commercials on Gamma Live
model.addConstr(
    NumCommercialsGammaLive * (1 - MaxPropGammaLive) 
    <= MaxPropGammaLive * (NumCommercialsPiTV + NumCommercialsBetaVideo), 
    name="max_commercials_gamma_live"
)

# Add constraint for the minimum proportion of commercials on Pi TV
model.addConstr((1 - MinPropPiTV) * NumCommercialsPiTV >= MinPropPiTV * (NumCommercialsBetaVideo + NumCommercialsGammaLive), name="min_proportion_PiTV")

# Add total cost constraint within the weekly budget
model.addConstr(
    (NumCommercialsPiTV * CostPiTV) + 
    (NumCommercialsBetaVideo * CostBetaVideo) + 
    (NumCommercialsGammaLive * CostGammaLive) <= WeeklyBudget, 
    name="total_cost_constraint"
)

# Add constraint for total advertising cost not exceeding the weekly budget
model.addConstr(
    NumCommercialsPiTV * CostPiTV + NumCommercialsBetaVideo * CostBetaVideo + NumCommercialsGammaLive * CostGammaLive <= WeeklyBudget,
    name="total_advertising_cost_constraint"
)

# Add constraint to ensure the number of commercials on Beta Video does not exceed the maximum allowed
model.addConstr(NumCommercialsBetaVideo <= MaxCommercialsBetaVideo, name="max_commercials_beta_video")

# Add constraint to ensure the number of commercials on Gamma Live does not exceed 33% of the total.
model.addConstr(NumCommercialsGammaLive <= MaxPropGammaLive * (NumCommercialsPiTV + NumCommercialsBetaVideo + NumCommercialsGammaLive), name="GammaLive_commercials_limit")

# Add constraint to ensure the number of commercials on Pi TV is at least 20% of total commercials
model.addConstr(NumCommercialsPiTV >= MinPropPiTV * (NumCommercialsPiTV + NumCommercialsBetaVideo + NumCommercialsGammaLive), 
                name="MinCommericalsOnPiTV")

# Add non-negativity constraints for decision variables
model.addConstr(NumCommercialsPiTV >= 0, name="nonnegativity_NumCommercialsPiTV")
model.addConstr(NumCommercialsBetaVideo >= 0, name="nonnegativity_NumCommercialsBetaVideo")
model.addConstr(NumCommercialsGammaLive >= 0, name="nonnegativity_NumCommercialsGammaLive")

# Set objective
model.setObjective(
    ReachPiTV * NumCommercialsPiTV 
    + ReachBetaVideo * NumCommercialsBetaVideo 
    + ReachGammaLive * NumCommercialsGammaLive,
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
