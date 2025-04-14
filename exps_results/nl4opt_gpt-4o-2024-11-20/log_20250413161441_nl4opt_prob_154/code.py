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
NumSmallTeams = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumSmallTeams")
NumLargeTeams = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumLargeTeams")

# Add constraint for total employees assigned to small and large teams
model.addConstr(SmallTeamEmployees * NumSmallTeams + LargeTeamEmployees * NumLargeTeams <= TotalEmployees, name="employee_allocation")

# Non-negativity of NumSmallTeams is enforced implicitly by the variable's default lower bound (0 in gurobipy).

# The non-negativity is already ensured by defining NumLargeTeams as a continuous variable (default lower bound is 0)

# Add constraint ensuring the number of small teams is at least MinRatioSmallToLarge times the number of large teams
model.addConstr(NumSmallTeams >= MinRatioSmallToLarge * NumLargeTeams, name="small_to_large_team_ratio")

# Ensure at least MinLargeTeams large teams are used for mowing lawns
model.addConstr(NumLargeTeams >= MinLargeTeams, name="min_large_teams")

# Add the constraint that the number of small teams must be at least the minimum specified
model.addConstr(NumSmallTeams >= MinSmallTeams, name="min_small_teams")

# Add constraint for total employees used by small and large teams
model.addConstr(
    SmallTeamEmployees * NumSmallTeams + LargeTeamEmployees * NumLargeTeams <= TotalEmployees,
    name="total_employee_capacity"
)

# Add constraint ensuring the number of small teams meets the minimum required
model.addConstr(NumSmallTeams >= MinSmallTeams, name="min_small_teams_constraint")

# Add constraint ensuring the number of large teams meets the minimum required
model.addConstr(NumLargeTeams >= MinLargeTeams, name="min_large_teams_constraint")

# Add constraint to ensure the ratio of small to large teams meets the minimum
model.addConstr(NumSmallTeams >= MinRatioSmallToLarge * NumLargeTeams, name="min_small_to_large_ratio")

# Set objective
model.setObjective(SmallTeamArea * NumSmallTeams + LargeTeamArea * NumLargeTeams, gp.GRB.MAXIMIZE)

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
