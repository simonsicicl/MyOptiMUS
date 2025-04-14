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
NumberOfThrowingGames = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfThrowingGames")
NumberOfClimbingGames = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfClimbingGames")



# Ensure there are at least a minimum number of climbing games operated in the amusement park
model.addConstr(NumberOfClimbingGames >= MinClimbingGames, name="min_climbing_games_constraint")

# Total cost of prizes for throwing and climbing games per hour does not exceed MaxPrizeCost
model.addConstr(NumberOfThrowingGames * Ct * Pt + NumberOfClimbingGames * Cc * Pc <= MaxPrizeCost, "Max_Prize_Cost_Constraint")

model.addConstr(NumberOfThrowingGames >= 0, "NumberOfThrowingGames_non_negative")

# Ensure the number of climbing games is non-negative and satisfies the minimum requirement
model.addConstr(NumberOfClimbingGames >= MinClimbingGames, name="min_climbing_games")

# Ensure there are more throwing games than climbing games by a minimum ratio R
model.addConstr(NumberOfThrowingGames >= R * NumberOfClimbingGames, name="MinRatioThrowingClimbingGames")

# Ensure that the total cost of prizes per hour does not exceed the maximum allowed.
model.addConstr(Pt * NumberOfThrowingGames + Pc * NumberOfClimbingGames <= MaxPrizeCost, name="max_prize_cost_constraint")

# Ensure at least the minimum number of climbing games is operated
model.addConstr(NumberOfClimbingGames >= MinClimbingGames, name="min_climbing_games")

# Define the model
model = gp.Model("AmusementParkOptimization")

# Variables
NumberOfThrowingGames = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfThrowingGames")
NumberOfClimbingGames = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfClimbingGames")

# Parameters
Ct = 15 # Number of customers per hour for throwing games
Cc = 8  # Number of customers per hour for climbing games

# Objective function
model.setObjective(Ct * NumberOfThrowingGames + Cc * NumberOfClimbingGames, gp.GRB.MAXIMIZE)

# Update the model
model.update()

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
