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
ProcessJOperations = model.addVar(vtype=gp.GRB.INTEGER, name="ProcessJOperations")
ProcessPOperations = model.addVar(vtype=gp.GRB.INTEGER, name="ProcessPOperations")

# Since ProcessJOperations is already defined as a non-negative integer variable, no additional constraint is needed
# ProcessJOperations >= 0 is inherently satisfied by the variable definition

model.addConstr(ProcessPOperations >= 0, name="ProcessPOperations_nonnegativity")

# Total water usage constraint for both processes J and P
model.addConstr(WaterJ * ProcessJOperations + WaterP * ProcessPOperations <= MaxWater, name="Total_Water_Usage")

# Define the total pollution constraint
model.addConstr((PollutionJ * ProcessJOperations) + (PollutionP * ProcessPOperations) <= MaxPollution, name="total_pollution_limit")

# Total water usage by process J and P should not exceed the maximum units of water available
model.addConstr(WaterJ * ProcessJOperations + WaterP * ProcessPOperations <= MaxWater, name="total_water_usage")

# Add pollution constraint
model.addConstr(PollutionJ * ProcessJOperations + PollutionP * ProcessPOperations <= MaxPollution, name="pollution_limit")

# Define objective function
model.setObjective(MetalJ * ProcessJOperations + MetalP * ProcessPOperations, gp.GRB.MAXIMIZE)

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
