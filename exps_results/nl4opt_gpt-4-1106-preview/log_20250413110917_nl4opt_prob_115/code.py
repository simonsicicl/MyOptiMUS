import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_115/data.json", "r") as f:
    data = json.load(f)

TimeFertilizer = data["TimeFertilizer"] # scalar parameter
TimeSeeds = data["TimeSeeds"] # scalar parameter
MaxUnits = data["MaxUnits"] # scalar parameter
MinFertilizer = data["MinFertilizer"] # scalar parameter
MaxFertilizerSeedRatio = data["MaxFertilizerSeedRatio"] # scalar parameter
FertilizerUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FertilizerUnits")
SeedUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SeedUnits")
TotalEffectiveTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalEffectiveTime")

# Add constraint for the maximum units of fertilizer and seeds combined
model.addConstr(FertilizerUnits + SeedUnits <= MaxUnits, name="Max_Fertilizer_and_Seed_Units")

# Add constraint for minimum required units of fertilizer
model.addConstr(FertilizerUnits >= MinFertilizer, name="min_fertilizer_requirement")

# Amount of fertilizer cannot exceed MaxFertilizerSeedRatio times the amount of seeds constraint
model.addConstr(FertilizerUnits <= MaxFertilizerSeedRatio * SeedUnits, name="fertilizer_seed_ratio")

# Add non-negativity constraint for the number of units of fertilizer
model.addConstr(FertilizerUnits >= 0, name="nonnegativity_fertilizer")

# Add non-negativity constraint for the number of units of seeds
model.addConstr(SeedUnits >= 0, name="seed_units_nonnegativity")

# Add constraint for the total effective time
model.addConstr(TotalEffectiveTime == TimeFertilizer * FertilizerUnits + TimeSeeds * SeedUnits, name="total_effective_time")

# Add constraint: Total units of fertilizer and seeds do not exceed maximum combined units
model.addConstr(FertilizerUnits + SeedUnits <= MaxUnits, name="max_fertilizer_seed_units")

# Add constraint to ensure the minimum required units of fertilizer is used
model.addConstr(FertilizerUnits >= MinFertilizer, name="min_fertilizer_usage")

# Constraint: The ratio of fertilizer to seeds does not exceed the maximum allowed value
model.addConstr(FertilizerUnits <= MaxFertilizerSeedRatio * SeedUnits, "max_fertilizer_seed_ratio")

# Set objective
model.setObjective(TotalEffectiveTime, gp.GRB.MINIMIZE)

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
