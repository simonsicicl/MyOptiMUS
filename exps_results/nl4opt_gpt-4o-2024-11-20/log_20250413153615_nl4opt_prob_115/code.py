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
UnitsFertilizer = model.addVar(vtype=gp.GRB.CONTINUOUS, name="UnitsFertilizer")
UnitsSeeds = model.addVar(vtype=gp.GRB.CONTINUOUS, name="UnitsSeeds")
AuxSeedNonzero = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AuxSeedNonzero")
MaxEffectiveTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MaxEffectiveTime")
AuxSeedNonzero = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AuxSeedNonzero")

# Add constraint for the combined units of fertilizer and seeds
model.addConstr(UnitsFertilizer + UnitsSeeds <= MaxUnits, name="fertilizer_seeds_limit")

# Add constraint ensuring at least MinFertilizer units of fertilizer are applied
model.addConstr(UnitsFertilizer >= MinFertilizer, name="fertilizer_minimum")

# Fertilizer to seed ratio constraint
model.addConstr(UnitsFertilizer <= MaxFertilizerSeedRatio * UnitsSeeds, name="fertilizer_seed_ratio")

# Add fertilizer and seed application constraints
model.addConstr(UnitsFertilizer >= 0, name="nonnegative_fertilizer")
model.addConstr(UnitsSeeds >= 0, name="nonnegative_seeds")
model.addConstr(UnitsFertilizer + UnitsSeeds <= MaxUnits, name="combined_units_limit")
model.addConstr(UnitsFertilizer >= MinFertilizer, name="min_fertilizer_limit")
model.addConstr(UnitsFertilizer <= MaxFertilizerSeedRatio * UnitsSeeds + AuxSeedNonzero, name="fertilizer_seed_ratio_limit")

# The non-negativity constraint is implicitly satisfied as Gurobi variables are non-negative by default unless otherwise specified (e.g., with lower bounds of negative values).

# Add constraint to ensure fertilizer units meet the minimum required amount
model.addConstr(UnitsFertilizer >= MinFertilizer, name="fertilizer_minimum_requirement")

# Add constraint for fertilizer-to-seeds ratio
model.addConstr(UnitsFertilizer <= MaxFertilizerSeedRatio * UnitsSeeds, name="fertilizer_seed_ratio")

# Add auxiliary constraints to ensure UnitsSeeds is non-zero
model.addConstr(AuxSeedNonzero >= 0, name="AuxSeedNonzero_geq_0")
model.addConstr(AuxSeedNonzero >= -MaxFertilizerSeedRatio * UnitsSeeds, name="AuxSeedNonzero_geq_-MaxFertilizerSeedRatio_times_UnitsSeeds")

# Add constraint to ensure maximum effective time is greater than or equal to the effective time for fertilizer
model.addConstr(MaxEffectiveTime >= UnitsFertilizer * TimeFertilizer, name="max_effective_time_constraint")

# Add constraint to ensure maximum effective time is greater than or equal to effective time for seeds
model.addConstr(MaxEffectiveTime >= UnitsSeeds * TimeSeeds, name="max_effective_time_constraint")

# Add constraint: Total fertilizer and seed units cannot exceed maximum allowed units
model.addConstr(UnitsFertilizer + UnitsSeeds <= MaxUnits, name="fertilizer_seed_limit")

# Add constraint to ensure applied fertilizer is greater than or equal to the minimum required
model.addConstr(UnitsFertilizer >= MinFertilizer, name="min_fertilizer_requirement")

# Add fertilizer-to-seeds ratio constraint
model.addConstr(UnitsFertilizer <= MaxFertilizerSeedRatio * AuxSeedNonzero, name="fertilizer_seed_ratio")

# Add constraint to ensure AuxSeedNonzero is at least 1 or equal to UnitsSeeds
model.addConstr(AuxSeedNonzero >= UnitsSeeds, name="aux_seed_nonzero_constraint")

# Add constraint for ensuring AuxSeedNonzero is at least 1
model.addConstr(AuxSeedNonzero >= 1, name="AuxSeedNonzero_minimum")

# Set objective to minimize MaxEffectiveTime
model.setObjective(MaxEffectiveTime, gp.GRB.MINIMIZE)

# Add constraints ensuring MaxEffectiveTime is greater than or equal to each individual effective time
model.addConstr(MaxEffectiveTime >= TimeFertilizer * UnitsFertilizer, name="EffectiveTimeFertilizer")
model.addConstr(MaxEffectiveTime >= TimeSeeds * UnitsSeeds, name="EffectiveTimeSeeds")

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
