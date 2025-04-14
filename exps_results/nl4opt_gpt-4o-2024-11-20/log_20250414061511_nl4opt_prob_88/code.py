import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_88/data.json", "r") as f:
    data = json.load(f)

VolumeGlass = data["VolumeGlass"] # scalar parameter
VolumePlastic = data["VolumePlastic"] # scalar parameter
RatioPlasticToGlass = data["RatioPlasticToGlass"] # scalar parameter
MinGlassBottles = data["MinGlassBottles"] # scalar parameter
TotalWaterVolume = data["TotalWaterVolume"] # scalar parameter
NumberGlassBottles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberGlassBottles")
NumberPlasticBottles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberPlasticBottles")

# The non-negativity of NumberGlassBottles is inherently ensured as it is defined as a continuous variable in gurobipy, which defaults to having a non-negative lower bound.

# Ensure the number of plastic bottles is non-negative
model.addConstr(NumberPlasticBottles >= 0, name="non_negative_plastic_bottles")

# Add total water volume constraint
model.addConstr(NumberGlassBottles * VolumeGlass + NumberPlasticBottles * VolumePlastic <= TotalWaterVolume, name="water_volume_constraint")

# Add constraint for the minimum ratio of plastic bottles to glass bottles
model.addConstr(NumberPlasticBottles >= RatioPlasticToGlass * NumberGlassBottles, name="plastic_to_glass_ratio")

# Add constraint to ensure the number of glass bottles produced meets the minimum requirement
model.addConstr(NumberGlassBottles >= MinGlassBottles, name="min_glass_bottles_constraint")

# Add constraint to ensure the total water used does not exceed available water volume
model.addConstr(
    NumberGlassBottles * VolumeGlass + NumberPlasticBottles * VolumePlastic <= TotalWaterVolume,
    name="water_usage_limit"
)

# Add constraint to ensure the ratio of plastic bottles to glass bottles meets or exceeds the minimum required ratio
model.addConstr(NumberPlasticBottles >= RatioPlasticToGlass * NumberGlassBottles, name="plastic_to_glass_ratio")

# Add constraint to ensure the production of glass bottles meets the minimum requirement
model.addConstr(NumberGlassBottles >= MinGlassBottles, name="min_glass_bottles")

# Set objective
model.setObjective(NumberGlassBottles + NumberPlasticBottles, gp.GRB.MAXIMIZE)

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
