import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_174/data.json", "r") as f:
    data = json.load(f)

SmallBinWorkers = data["SmallBinWorkers"] # scalar parameter
LargeBinWorkers = data["LargeBinWorkers"] # scalar parameter
SmallBinCapacity = data["SmallBinCapacity"] # scalar parameter
LargeBinCapacity = data["LargeBinCapacity"] # scalar parameter
TotalWorkers = data["TotalWorkers"] # scalar parameter
BinRatio = data["BinRatio"] # scalar parameter
MinSmallBins = data["MinSmallBins"] # scalar parameter
MinLargeBins = data["MinLargeBins"] # scalar parameter
NumSmallBins = model.addVar(vtype=gp.GRB.INTEGER, name="NumSmallBins")
NumLargeBins = model.addVar(vtype=gp.GRB.INTEGER, name="NumLargeBins")

TotalWorkersForSmallBins = model.addVar(vtype=gp.GRB.INTEGER, name="TotalWorkersForSmallBins")
model.addConstr(NumSmallBins * SmallBinWorkers == TotalWorkersForSmallBins, name="TotalWorkersForSmallBins")

# Add constraint to ensure each large bin requires LargeBinWorkers workers
model.addConstr(NumLargeBins * LargeBinWorkers <= TotalWorkers, name="large_bin_worker_requirement")

# Adding a constraint to ensure the total workers used does not exceed available workers
model.addConstr(
    SmallBinWorkers * NumSmallBins + LargeBinWorkers * NumLargeBins <= TotalWorkers,
    name="worker_limit"
)

# Add constraint ensuring number of small bins equals BinRatio times number of large bins
model.addConstr(NumSmallBins == BinRatio * NumLargeBins, name="small_to_large_bin_ratio")

# Add constraint to ensure the number of small bins used is at least the minimum required
model.addConstr(NumSmallBins >= MinSmallBins, name="min_small_bins")

# Add constraint ensuring the number of large bins used is at least MinLargeBins
model.addConstr(NumLargeBins >= MinLargeBins, name="min_large_bins")

# The variable NumSmallBins is already defined. No additional code is needed for this constraint as non-negativity is implicitly enforced by variable domain constraints in gurobipy.

# The constraint is implicitly satisfied as Gurobi variables are non-negative by default unless otherwise specified.

# Add constraint ensuring the minimum number of large bins
model.addConstr(NumLargeBins >= MinLargeBins, name="min_large_bins_constraint")

# Add worker assignment constraint
model.addConstr(
    SmallBinWorkers * NumSmallBins + LargeBinWorkers * NumLargeBins <= TotalWorkers,
    name="worker_assignment"
)

# Add constraint to enforce the ratio between small bins and large bins
model.addConstr(NumSmallBins == BinRatio * NumLargeBins, name="bin_ratio_constraint")

# Add constraint to ensure the number of small bins is greater than or equal to the minimum required
model.addConstr(NumSmallBins >= MinSmallBins, name="min_small_bins_constraint")

# Add constraint to ensure the number of large bins is greater than or equal to the minimum required
model.addConstr(NumLargeBins >= MinLargeBins, name="min_large_bins_constraint")

# Set objective
model.setObjective(SmallBinCapacity * NumSmallBins + LargeBinCapacity * NumLargeBins, gp.GRB.MAXIMIZE)

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
