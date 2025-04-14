import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_155/data.json", "r") as f:
    data = json.load(f)

OtterTricks = data["OtterTricks"] # scalar parameter
OtterTreats = data["OtterTreats"] # scalar parameter
DolphinTricks = data["DolphinTricks"] # scalar parameter
DolphinTreats = data["DolphinTreats"] # scalar parameter
MinDolphins = data["MinDolphins"] # scalar parameter
MaxOtterProportion = data["MaxOtterProportion"] # scalar parameter
TotalTreats = data["TotalTreats"] # scalar parameter
NumberOfOtters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfOtters")
NumberOfDolphins = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfDolphins")
TotalPerformers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalPerformers")

# The variable "NumberOfOtters" is non-negative due to its default lower bound (0) in Gurobi, no additional constraint is needed.

# The variable NumberOfDolphins is already defined as non-negative because it is continuous by default in Gurobi (vtype=gp.GRB.CONTINUOUS).

# Add constraint to ensure the number of dolphins used in the show is at least the minimum required
model.addConstr(NumberOfDolphins >= MinDolphins, name="min_dolphins_constraint")

# Add constraint to enforce that at most MaxOtterProportion of performers are otters
model.addConstr(
    NumberOfOtters <= (MaxOtterProportion / (1 - MaxOtterProportion)) * NumberOfDolphins, 
    name="max_otter_proportion"
)

# Add constraint for total treats used by otters and dolphins
model.addConstr(NumberOfOtters * OtterTreats + NumberOfDolphins * DolphinTreats <= TotalTreats, name="treats_limit")

# Add constraint to ensure total treats used do not exceed available treats
model.addConstr(3 * NumberOfOtters + 5 * NumberOfDolphins <= TotalTreats, name="treat_limit")

# Add constraint to ensure the number of dolphins meets the minimum required
model.addConstr(NumberOfDolphins >= MinDolphins, name="min_dolphins_constraint")

# Add constraint: NumberOfOtters must be at most the allowed proportion of TotalPerformers
model.addConstr(NumberOfOtters <= MaxOtterProportion * TotalPerformers, name="otter_proportion_limit")

# Add constraint: TotalPerformers equals the sum of NumberOfOtters and NumberOfDolphins
model.addConstr(TotalPerformers == NumberOfOtters + NumberOfDolphins, name="total_performers_constraint")

# Set objective
model.setObjective(3 * NumberOfOtters + 1 * NumberOfDolphins, gp.GRB.MAXIMIZE)

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
