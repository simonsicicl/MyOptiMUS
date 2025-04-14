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
TotalLargeBinWorkers = model.addVar(vtype=gp.GRB.INTEGER, name="TotalLargeBinWorkers")
NumLargeBins = model.addVar(vtype=gp.GRB.INTEGER, name="NumLargeBins")

# Add constraint that each small bin requires a fixed number of workers
model.addConstr(NumSmallBins * SmallBinWorkers <= TotalWorkers, "worker_constraint_for_small_bins")

# Ensure the total number of workers for large bins does not exceed the total available workers
model.addConstr(TotalLargeBinWorkers <= TotalWorkers, name="large_bin_workers_constraint")

# Add constraint for the total number of workers used cannot exceed the total number of workers available
model.addConstr(NumSmallBins * SmallBinWorkers + TotalLargeBinWorkers <= TotalWorkers, name="worker_limit")

# Constraint: Number of small bins must be BinRatio times the number of large bins
model.addConstr(NumSmallBins == BinRatio * NumLargeBins, name="small_large_bin_ratio")

# Add constraint to ensure the minimum number of small bins is used
model.addConstr(NumSmallBins >= MinSmallBins, name="min_small_bins")

# Add constraint to ensure the minimum number of large bins is used
model.addConstr(NumLargeBins >= MinLargeBins, name="min_large_bins")

# The number of small bins is non-negative. Since the variable is defined as an integer, no need to add a constraint.
# The integrality constraint is encoded in the variable definition, ensuring NumSmallBins >= 0.

# Since NumLargeBins has already been added as an integer variable and we want it to be non-negative,
# we don't need to add a constraint for NumLargeBins >= 0 because Gurobi integer variables are
# non-negative by default.

# Constraint for calculating the total number of workers required for large bins
model.addConstr(TotalLargeBinWorkers == NumLargeBins * LargeBinWorkers, name="total_large_bin_workers")



# Link the TotalLargeBinWorkers variable with NumLargeBins and corresponding workers needed
model.addConstr(TotalLargeBinWorkers == LargeBinWorkers * NumLargeBins, name="link_large_bin_workers")

# Maintain the ratio of the number of small bins to large bins
model.addConstr(NumSmallBins <= BinRatio * NumLargeBins, name="bin_ratio_constraint")

# Ensure the minimum number of small bins is maintained
model.addConstr(NumSmallBins >= MinSmallBins, "min_small_bins_constraint")

# Ensure the minimum number of large bins is maintained
model.addConstr(NumLargeBins >= MinLargeBins, "min_large_bins_constraint")

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
