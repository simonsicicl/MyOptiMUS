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
LongCables = model.addVar(vtype=gp.GRB.INTEGER, name="LongCables")
ShortCables = model.addVar(vtype=gp.GRB.INTEGER, name="ShortCables")

# Constraint for the minimum number of long cables
model.addConstr(LongCables >= MinLong, name="min_long_cables")

# The variable ShortCables is already defined as an integer, no additional constraint is needed

# Add constraint to ensure the number of long cables is non-negative
model.addConstr(LongCables >= 0, name="non_negative_long_cables")

# Add constraint to ensure the number of short cables is non-negative
model.addConstr(ShortCables >= 0, name="short_cables_non_negative")

# Ensure total gold used does not exceed the available gold
model.addConstr(GoldLong * LongCables + GoldShort * ShortCables <= TotalGold, name="gold_usage")

# Add constraint to ensure the number of short cables is at least RatioShortLong times the number of long cables
model.addConstr(ShortCables >= RatioShortLong * LongCables, name="Short_to_Long_Ratio")

# Ensure the number of long cables is at least the minimum required
model.addConstr(LongCables >= MinLong, name="min_long_cables_constraint")

# Add gold availability constraint for long and short cables
model.addConstr(GoldLong * LongCables + GoldShort * ShortCables <= TotalGold, name="gold_availability")

# Add constraint for the number of short cables to be at least five times the number of long cables
model.addConstr(ShortCables >= RatioShortLong * LongCables, name="Short_to_Long_Cable_Ratio")

# Total use of gold does not exceed the available amount constraint
model.addConstr(GoldLong * LongCables + GoldShort * ShortCables <= TotalGold, "gold_usage")

# Ensure the ratio of short cables to long cables is maintained
model.addConstr(ShortCables >= RatioShortLong * LongCables, name="short_long_ratio")

# Add constraint to ensure the minimum number of long cables is produced
model.addConstr(LongCables >= MinLong, name="min_long_cables")

# Set the objective function
model.setObjective(ProfitLong * LongCables + ProfitShort * ShortCables, gp.GRB.MAXIMIZE)

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
