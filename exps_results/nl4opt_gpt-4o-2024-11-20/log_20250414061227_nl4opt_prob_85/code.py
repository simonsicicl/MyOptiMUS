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
NetAcres = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NetAcres")
LineAcres = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LineAcres")

# Add constraint to ensure total acres used for net and line fishing do not exceed lake size
model.addConstr(NetAcres + LineAcres <= LakeSize, name="fishing_acre_limit")

# Add constraint to ensure the number of acres fished with a net is non-negative
model.addConstr(NetAcres >= 0, name="non_negative_net_acres")

# Add constraint to ensure the acres fished with a line is non-negative
model.addConstr(LineAcres >= 0, name="non_negative_LineAcres")

# Add bait usage constraint
model.addConstr(BaitNet * NetAcres + BaitLine * LineAcres <= TotalBait, name="bait_usage")

# Add pain tolerance constraint
model.addConstr(PainNet * NetAcres + PainLine * LineAcres <= MaxPain, name="pain_tolerance")

# Add lake size constraint ensuring total acres used for fishing do not exceed the lake size
model.addConstr(NetAcres + LineAcres <= LakeSize, name="lake_size_constraint")

# Add bait availability constraint
model.addConstr(BaitNet * NetAcres + BaitLine * LineAcres <= TotalBait, name="bait_availability")

# Add pain tolerance constraint
model.addConstr(PainNet * NetAcres + PainLine * LineAcres <= MaxPain, name="pain_tolerance")

# Non-negativity constraint for NetAcres
model.addConstr(NetAcres >= 0, name="non_negativity_NetAcres")

# Ensure the non-negativity of LineAcres
model.addConstr(LineAcres >= 0, name="non_negativity_LineAcres")

# Set objective
model.setObjective(FishNet * NetAcres + FishLine * LineAcres, gp.GRB.MAXIMIZE)

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
