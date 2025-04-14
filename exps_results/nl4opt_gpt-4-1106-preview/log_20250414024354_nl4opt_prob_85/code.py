import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_85/data.json", "r") as f:
    data = json.load(f)

LakeSize = data["LakeSize"] # scalar parameter
FishNet = data["FishNet"] # scalar parameter
FishLine = data["FishLine"] # scalar parameter
BaitNet = data["BaitNet"] # scalar parameter
BaitLine = data["BaitLine"] # scalar parameter
PainNet = data["PainNet"] # scalar parameter
PainLine = data["PainLine"] # scalar parameter
TotalBait = data["TotalBait"] # scalar parameter
MaxPain = data["MaxPain"] # scalar parameter
AcresNet = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AcresNet")
AcresLine = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AcresLine")

# Add lake size constraint for fishing with net and line
model.addConstr(AcresNet + AcresLine <= LakeSize, name="lake_size_constraint")

# Add non-negativity constraint for AcresNet
model.addConstr(AcresNet >= 0, name="nonnegativity_acres_net")

# Add non-negativity constraint for AcresLine
model.addConstr(AcresLine >= 0, name="nonnegativity_acres_line")

# Add constraint for total amount of bait used for fishing with a net and a line
model.addConstr(BaitNet * AcresNet + BaitLine * AcresLine <= TotalBait, name="bait_limit")

# Total pain experienced by the fisherman constraint
model.addConstr(AcresNet * PainNet + AcresLine * PainLine <= MaxPain, name="fisherman_pain_tolerance")

# Constraint: The total acres used for both fishing with a net and fishing line cannot exceed the total lake size
model.addConstr(AcresNet + AcresLine <= LakeSize, name="lake_size_limit")

# Add constraint for the total amount of bait used
model.addConstr(BaitNet * AcresNet + BaitLine * AcresLine <= TotalBait, name="bait_limit")

# Add pain tolerance constraint
model.addConstr((PainNet * AcresNet) + (PainLine * AcresLine) <= MaxPain, name="pain_tolerance")

# Set objective
model.setObjective(FishNet * AcresNet + FishLine * AcresLine, gp.GRB.MAXIMIZE)

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
