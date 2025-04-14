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
NumGlassBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumGlassBottles")
NumPlasticBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumPlasticBottles")

# Add non-negativity constraint for glass bottles
model.addConstr(NumGlassBottles >= 0, name="non_negativity_glass_bottles")

# Add constraint to ensure the number of plastic bottles produced is non-negative
model.addConstr(NumPlasticBottles >= 0, name="non_negativity_NumPlasticBottles")

# Add constraint for the total volume of water in bottles not to exceed available water volume
model.addConstr(VolumeGlass * NumGlassBottles + VolumePlastic * NumPlasticBottles <= TotalWaterVolume, "total_water_volume_constraint")

# Add constraint: Number of plastic bottles must be at least RatioPlasticToGlass times the number of glass bottles
model.addConstr(NumPlasticBottles >= RatioPlasticToGlass * NumGlassBottles, "plastic_to_glass_ratio")

# Ensure the production of at least the minimum number of glass bottles
model.addConstr(NumGlassBottles >= MinGlassBottles, "min_glass_bottles")

# Ensure the volume of water used does not exceed the total available water volume
model.addConstr(VolumeGlass * NumGlassBottles + VolumePlastic * NumPlasticBottles <= TotalWaterVolume, name="water_volume_constraint")

# Ensure minimum required production of glass bottles
model.addConstr(NumGlassBottles >= MinGlassBottles, name="min_glass_bottles")

# Maintain the minimum ratio constraint of plastic bottles to glass bottles
model.addConstr(NumPlasticBottles >= RatioPlasticToGlass * NumGlassBottles, "min_ratio_plastic_to_glass")

# Set objective
model.setObjective(NumGlassBottles + NumPlasticBottles, gp.GRB.MAXIMIZE)

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
