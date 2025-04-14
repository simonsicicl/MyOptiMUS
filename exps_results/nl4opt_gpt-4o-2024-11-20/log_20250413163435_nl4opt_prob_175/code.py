import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_175/data.json", "r") as f:
    data = json.load(f)

SeasonalPoints = data["SeasonalPoints"] # scalar parameter
FullTimePoints = data["FullTimePoints"] # scalar parameter
MaxPoints = data["MaxPoints"] # scalar parameter
GiftsPerSeasonal = data["GiftsPerSeasonal"] # scalar parameter
GiftsPerFullTime = data["GiftsPerFullTime"] # scalar parameter
MaxSeasonalPercent = data["MaxSeasonalPercent"] # scalar parameter
MinFullTimeVolunteers = data["MinFullTimeVolunteers"] # scalar parameter
SeasonalVolunteers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SeasonalVolunteers")
FullTimeVolunteers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FullTimeVolunteers")

# Adding the constraint for total seasonal points
model.addConstr(SeasonalVolunteers * SeasonalPoints <= MaxPoints, name="seasonal_points_constraint")

# Add constraint to ensure total points from full-time volunteers does not exceed MaxPoints
model.addConstr(FullTimePoints * FullTimeVolunteers <= MaxPoints, name="FullTimePoints_Limit")

# Add constraint to limit the percentage of seasonal volunteers
model.addConstr((1 - MaxSeasonalPercent) * SeasonalVolunteers <= MaxSeasonalPercent * FullTimeVolunteers, 
                name="limit_seasonal_volunteers")

# Add constraint to ensure the number of full-time volunteers is at least the minimum required
model.addConstr(FullTimeVolunteers >= MinFullTimeVolunteers, name="min_full_time_volunteers")

# Adding constraint for total points used by volunteers
model.addConstr(
    SeasonalPoints * SeasonalVolunteers + FullTimePoints * FullTimeVolunteers <= MaxPoints,
    name="points_budget_constraint"
)

# Add constraint for maximum percentage of seasonal volunteers
model.addConstr((1 - MaxSeasonalPercent) * SeasonalVolunteers <= MaxSeasonalPercent * FullTimeVolunteers, 
                name="max_seasonal_volunteers")

# Add minimum full-time volunteers constraint
model.addConstr(FullTimeVolunteers >= MinFullTimeVolunteers, name="min_full_time_volunteers")

# Set objective
model.setObjective(GiftsPerSeasonal * SeasonalVolunteers + GiftsPerFullTime * FullTimeVolunteers, gp.GRB.MAXIMIZE)

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
