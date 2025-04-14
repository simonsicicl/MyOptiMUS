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
SeasonalVolunteers = model.addVar(vtype=gp.GRB.INTEGER, name="SeasonalVolunteers")
FullTimeVolunteers = model.addVar(vtype=gp.GRB.INTEGER, name="FullTimeVolunteers")

# Add constraint: Total points awarded to seasonal volunteers cannot exceed MaxPoints
model.addConstr(SeasonalVolunteers * SeasonalPoints <= MaxPoints, name="max_seasonal_points")

FullTimePoints = data["FullTimePoints"]  # scalar parameter
MaxPoints = data["MaxPoints"]  # scalar parameter
FullTimeVolunteers = model.addVar(vtype=gp.GRB.INTEGER, name="FullTimeVolunteers")

# Constraint: Total points awarded to full-time volunteers cannot exceed MaxPoints
model.addConstr(FullTimePoints * FullTimeVolunteers <= MaxPoints, name="FullTimeVolunteerPointsLimit")

model.addConstr(SeasonalVolunteers <= MaxSeasonalPercent * (SeasonalVolunteers + FullTimeVolunteers), 'max_seasonal_volunteers_percent_constraint')

# Constraint for minimum number of full-time volunteers
model.addConstr(FullTimeVolunteers >= MinFullTimeVolunteers, name="min_full_time_volunteers")

# Total points allocated to volunteers should not exceed the maximum available points
model.addConstr(SeasonalPoints * SeasonalVolunteers + FullTimePoints * FullTimeVolunteers <= MaxPoints, name="max_points_allocation")

# Add constraint for the number of seasonal volunteers not to exceed the predetermined percentage of the total number of volunteers
model.addConstr(SeasonalVolunteers <= MaxSeasonalPercent * (SeasonalVolunteers + FullTimeVolunteers), name="max_seasonal_volunteers")

# Ensure the number of full-time volunteers meets or exceeds the minimum required number
model.addConstr(FullTimeVolunteers >= MinFullTimeVolunteers, name="min_full_time_volunteers")

# Define the objective function
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
