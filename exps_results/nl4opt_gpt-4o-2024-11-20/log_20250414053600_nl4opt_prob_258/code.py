import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_258/data.json", "r") as f:
    data = json.load(f)

MetalJ = data["MetalJ"] # scalar parameter
WaterJ = data["WaterJ"] # scalar parameter
PollutionJ = data["PollutionJ"] # scalar parameter
MetalP = data["MetalP"] # scalar parameter
WaterP = data["WaterP"] # scalar parameter
PollutionP = data["PollutionP"] # scalar parameter
MaxWater = data["MaxWater"] # scalar parameter
MaxPollution = data["MaxPollution"] # scalar parameter
NumProcessJ = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumProcessJ")
NumProcessP = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumProcessP")

# Non-negativity constraint for the number of operations involving process J
model.addConstr(NumProcessJ >= 0, name="non_negative_NumProcessJ")

# Add constraint to ensure the number of operations involving process P is non-negative
model.addConstr(NumProcessP >= 0, name="non_negative_NumProcessP")

# Add constraint for total water usage
model.addConstr((WaterJ * NumProcessJ) + (WaterP * NumProcessP) <= MaxWater, name="water_usage")

# Add pollution limit constraint
model.addConstr(
    PollutionJ * NumProcessJ + PollutionP * NumProcessP <= MaxPollution,
    name="pollution_limit"
)

# Add water usage constraint
model.addConstr(WaterJ * NumProcessJ + WaterP * NumProcessP <= MaxWater, name="water_usage")

# Add pollution limit constraint
model.addConstr(PollutionJ * NumProcessJ + PollutionP * NumProcessP <= MaxPollution, name="pollution_limit")

# Non-negativity constraint for the number of operations for process J
model.addConstr(NumProcessJ >= 0, name="non_negative_NumProcessJ")

# Non-negativity constraint for the number of operations for process P
model.addConstr(NumProcessP >= 0, name="non_negative_NumProcessP")

# Set objective
model.setObjective(MetalJ * NumProcessJ + MetalP * NumProcessP, gp.GRB.MAXIMIZE)

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
