import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_14/data.json", "r") as f:
    data = json.load(f)

TotalGold = data["TotalGold"] # scalar parameter
GoldLong = data["GoldLong"] # scalar parameter
GoldShort = data["GoldShort"] # scalar parameter
RatioShortLong = data["RatioShortLong"] # scalar parameter
MinLong = data["MinLong"] # scalar parameter
ProfitLong = data["ProfitLong"] # scalar parameter
ProfitShort = data["ProfitShort"] # scalar parameter
NumLongCables = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumLongCables")
NumShortCables = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumShortCables")

# Update integrality for NumLongCables to integer
NumLongCables.vtype = gp.GRB.INTEGER

# Add minimum production constraint for long cables
model.addConstr(NumLongCables >= MinLong, name="min_long_cables")

# Add short-to-long cable ratio constraint
model.addConstr(NumShortCables >= RatioShortLong * NumLongCables, name="short_to_long_ratio")

# Add total gold availability constraint
model.addConstr(GoldLong * NumLongCables + GoldShort * NumShortCables <= TotalGold, name="gold_availability")

# Changing NumShortCables to be an integer variable
NumShortCables.vtype = gp.GRB.INTEGER

# Add constraint for non-negative production of long cables
model.addConstr(NumLongCables >= 0, name="non_negative_long_cables")

# Add constraint ensuring non-negative production for short cables
model.addConstr(NumShortCables >= 0, name="non_negative_short_cables")

# Add gold usage constraint
model.addConstr(GoldLong * NumLongCables + GoldShort * NumShortCables <= TotalGold, name="gold_usage_limit")

# Add constraint to ensure the number of short cables is at least RatioShortLong times the number of long cables
model.addConstr(NumShortCables >= RatioShortLong * NumLongCables, name="short_long_cable_ratio")

# Add constraint to ensure the number of long cables produced meets or exceeds MinLong
model.addConstr(NumLongCables >= MinLong, name="min_long_cable_production")

# Add constraint for minimum ratio of short cables to long cables
model.addConstr(NumShortCables >= RatioShortLong * NumLongCables, name="min_ratio_short_long")

# Add constraint: the number of long cables produced must meet the minimum production requirement
model.addConstr(NumLongCables >= MinLong, name="min_long_cables_requirement")

# Add constraint for the total gold required for production
model.addConstr(GoldLong * NumLongCables + GoldShort * NumShortCables <= TotalGold, name="gold_constraint")

# Add constraint ensuring NumShortCables is at least RatioShortLong times NumLongCables
model.addConstr(NumShortCables >= RatioShortLong * NumLongCables, name="min_short_to_long_ratio")

# Add constraint to ensure production meets minimum number of long cables
model.addConstr(NumLongCables >= MinLong, name="min_long_cable_constraint")

# Production quantities of long and short cables must be non-negative
model.addConstr(NumLongCables >= 0, name="NonNeg_LongCables")
model.addConstr(NumShortCables >= 0, name="NonNeg_ShortCables")

# Set objective
model.setObjective(ProfitLong * NumLongCables + ProfitShort * NumShortCables, gp.GRB.MAXIMIZE)

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
