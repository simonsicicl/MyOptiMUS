import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_231/data.json", "r") as f:
    data = json.load(f)

Ct = data["Ct"] # scalar parameter
Cc = data["Cc"] # scalar parameter
Pt = data["Pt"] # scalar parameter
Pc = data["Pc"] # scalar parameter
R = data["R"] # scalar parameter
MinClimbingGames = data["MinClimbingGames"] # scalar parameter
MaxPrizeCost = data["MaxPrizeCost"] # scalar parameter
T = model.addVar(vtype=gp.GRB.CONTINUOUS, name="T")
C = model.addVar(vtype=gp.GRB.CONTINUOUS, name="C")

# Add constraint for the number of throwing games being at least R times the number of climbing games
model.addConstr(T >= R * C, name="throwing_vs_climbing_games")

# Enforce minimum number of climbing games constraint
model.addConstr(C >= MinClimbingGames, name="min_climbing_games")

# Add constraint to ensure total prize cost per hour does not exceed MaxPrizeCost
model.addConstr(T * Pt + C * Pc <= MaxPrizeCost, name="prize_cost_limit")

# Add constraint for non-negative number of throwing games
model.addConstr(T >= 0, name="non_negative_throws")

# The number of climbing games must be non-negative
model.addConstr(C >= 0, name="non_negative_climbing_games")

# Add constraint: The number of throwing games must be at least R times the number of climbing games
model.addConstr(T >= R * C, name="throwing_vs_climbing_ratio")

# Enforce minimum number of climbing games constraint
model.addConstr(C >= MinClimbingGames, name="min_climbing_games")

# Add constraint for the total cost of prizes per hour
model.addConstr(T * Pt + C * Pc <= MaxPrizeCost, name="prize_cost_constraint")

# Set objective
model.setObjective(Ct * T + Cc * C, gp.GRB.MAXIMIZE)

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
