import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_154/data.json", "r") as f:
    data = json.load(f)

SmallTeamEmployees = data["SmallTeamEmployees"] # scalar parameter
SmallTeamArea = data["SmallTeamArea"] # scalar parameter
LargeTeamEmployees = data["LargeTeamEmployees"] # scalar parameter
LargeTeamArea = data["LargeTeamArea"] # scalar parameter
TotalEmployees = data["TotalEmployees"] # scalar parameter
MinRatioSmallToLarge = data["MinRatioSmallToLarge"] # scalar parameter
MinLargeTeams = data["MinLargeTeams"] # scalar parameter
MinSmallTeams = data["MinSmallTeams"] # scalar parameter
NumberOfSmallTeams = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallTeams")
NumberOfLargeTeams = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeTeams")

# Add constraint for the sum of employees in small and large teams
model.addConstr(SmallTeamEmployees * NumberOfSmallTeams + LargeTeamEmployees * NumberOfLargeTeams <= TotalEmployees, name="total_employees_constraint")

# Small teams employed constraint ensuring non-negativity
model.addConstr(NumberOfSmallTeams >= 0, name="non_negativity_small_teams")

# Add constraint to ensure the number of large teams is non-negative
model.addConstr(NumberOfLargeTeams >= 0, name="non_negative_large_teams")

# Constraint for minimum ratio of small to large teams
model.addConstr(NumberOfSmallTeams >= MinRatioSmallToLarge * NumberOfLargeTeams, name="min_ratio_small_large_teams")

# Add constraint for minimum number of large teams
model.addConstr(NumberOfLargeTeams >= MinLargeTeams, name="min_large_teams")

# Ensure the minimum number of small teams employed constraint
model.addConstr(NumberOfSmallTeams >= MinSmallTeams, name="min_small_teams")

# Set objective function
model.setObjective(NumberOfSmallTeams * SmallTeamArea + NumberOfLargeTeams * LargeTeamArea, gp.GRB.MAXIMIZE)

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
