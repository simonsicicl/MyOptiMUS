import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_180/data.json", "r") as f:
    data = json.load(f)

SmallKegCapacity = data["SmallKegCapacity"] # scalar parameter
LargeKegCapacity = data["LargeKegCapacity"] # scalar parameter
MaxSmallKegs = data["MaxSmallKegs"] # scalar parameter
MaxLargeKegs = data["MaxLargeKegs"] # scalar parameter
MaxKegsTransport = data["MaxKegsTransport"] # scalar parameter
MinLargeKegs = data["MinLargeKegs"] # scalar parameter
MinSmallLargeRatio = data["MinSmallLargeRatio"] # scalar parameter
NumberOfSmallKegs = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSmallKegs")
NumberOfLargeKegs = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeKegs")

# Constraint: Number of small kegs used must be non-negative
model.addConstr(NumberOfSmallKegs >= 0, name="non_negativity_small_kegs")

# Constraint: Number of large kegs used must be non-negative
model.addConstr(NumberOfLargeKegs >= 0, name="non_negative_large_kegs")

# Add constraint to ensure the number of small kegs used does not exceed the maximum available
model.addConstr(NumberOfSmallKegs <= MaxSmallKegs, name="max_small_kegs_constraint")

# Add constraint to ensure the number of large kegs used does not exceed availability
model.addConstr(NumberOfLargeKegs <= MaxLargeKegs, name="large_kegs_availability")

# Constraint: Number of small kegs should be at least MinSmallLargeRatio times as many as the number of large kegs
model.addConstr(NumberOfSmallKegs >= MinSmallLargeRatio * NumberOfLargeKegs, name="min_small_large_ratio_constraint")

# Add constraint for the maximum number of kegs that can be transported
model.addConstr(NumberOfSmallKegs + NumberOfLargeKegs <= MaxKegsTransport, name="MaxKegsTransport_Constraint")

# Add constraint for minimum number of large kegs used
model.addConstr(NumberOfLargeKegs >= MinLargeKegs, name="min_large_kegs")

# Define the objective function
model.setObjective(NumberOfSmallKegs * SmallKegCapacity + NumberOfLargeKegs * LargeKegCapacity, gp.GRB.MAXIMIZE)

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
