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
NumberOfCommercialsPiTV = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCommercialsPiTV")
NumberOfCommercialsBetaVideo = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCommercialsBetaVideo")
NumberOfCommercialsGammaLive = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCommercialsGammaLive")

# The number of commercials on any platform must be non-negative
model.addConstr(NumberOfCommercialsPiTV >= 0, name="nonnegativity_PiTV")
model.addConstr(NumberOfCommercialsBetaVideo >= 0, name="nonnegativity_BetaVideo")
model.addConstr(NumberOfCommercialsGammaLive >= 0, name="nonnegativity_GammaLive")

# Add constraint for the maximum number of commercials on Beta Video
model.addConstr(NumberOfCommercialsBetaVideo <= MaxCommercialsBetaVideo, "max_commercials_on_beta_video")

# Add constraint for the maximum proportion of commercials on Gamma Live
model.addConstr(NumberOfCommercialsGammaLive <= MaxPropGammaLive * (NumberOfCommercialsPiTV + NumberOfCommercialsBetaVideo + NumberOfCommercialsGammaLive), "MaxGammaLiveCommercials")

# Number of commercials on Pi TV is at least a certain proportion of the total number of commercials
model.addConstr(NumberOfCommercialsPiTV >= MinPropPiTV * (NumberOfCommercialsPiTV + NumberOfCommercialsBetaVideo + NumberOfCommercialsGammaLive), "MinProportionConstraintPiTV")

# Total cost of commercials constraint
model.addConstr(CostPiTV * NumberOfCommercialsPiTV + CostBetaVideo * NumberOfCommercialsBetaVideo + CostGammaLive * NumberOfCommercialsGammaLive <= WeeklyBudget, "Total_commercial_cost")

# Set the objective for maximizing total audience reach
model.setObjective(NumberOfCommercialsPiTV * ReachPiTV +
                   NumberOfCommercialsBetaVideo * ReachBetaVideo +
                   NumberOfCommercialsGammaLive * ReachGammaLive, gp.GRB.MAXIMIZE)

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
