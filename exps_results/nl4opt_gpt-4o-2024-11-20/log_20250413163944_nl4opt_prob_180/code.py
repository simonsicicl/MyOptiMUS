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
SmallKegsUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallKegsUsed")
LargeKegsUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeKegsUsed")

# The variable "SmallKegsUsed" is defined with non-negativity by default because it is continuous.
# No additional code is needed for this constraint.

# Since the variable "LargeKegsUsed" is already defined as non-negative (default property of Gurobi continuous variable), no constraint code is needed.

# Add constraint to ensure the number of small kegs used does not exceed the maximum allowable
model.addConstr(SmallKegsUsed <= MaxSmallKegs, name="limit_small_kegs")

# Add a constraint to ensure the number of large kegs used does not exceed the maximum allowable large kegs
model.addConstr(LargeKegsUsed <= MaxLargeKegs, name="max_large_kegs_constraint")

model.addConstr(SmallKegsUsed >= MinSmallLargeRatio * LargeKegsUsed, name="min_small_large_ratio_constraint")

# Add constraint to ensure the total number of small and large kegs transported does not exceed MaxKegsTransport
model.addConstr(SmallKegsUsed + LargeKegsUsed <= MaxKegsTransport, name="total_kegs_transport_constraint")

# Add constraint ensuring the number of large kegs used meets the minimum required
model.addConstr(LargeKegsUsed >= MinLargeKegs, name="min_large_kegs_constraint")

# Add constraint to ensure the number of small kegs used does not exceed the maximum available  
model.addConstr(SmallKegsUsed <= MaxSmallKegs, name="small_kegs_limit")

# Add constraint to ensure the number of large kegs used does not exceed the maximum available  
model.addConstr(LargeKegsUsed <= MaxLargeKegs, name="large_kegs_limit")

# Add constraint for maximum transportation capacity
model.addConstr(SmallKegsUsed + LargeKegsUsed <= MaxKegsTransport, name="max_transport_capacity")

# Add constraint to ensure the number of large kegs used is at least the minimum required
model.addConstr(LargeKegsUsed >= MinLargeKegs, name="min_large_kegs")

# Add constraint to ensure the number of small kegs used is at least the minimum ratio times the number of large kegs used
model.addConstr(SmallKegsUsed >= MinSmallLargeRatio * LargeKegsUsed, name="min_small_large_ratio")

# Set objective
model.setObjective(SmallKegsUsed * SmallKegCapacity + LargeKegsUsed * LargeKegCapacity, gp.GRB.MAXIMIZE)

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
