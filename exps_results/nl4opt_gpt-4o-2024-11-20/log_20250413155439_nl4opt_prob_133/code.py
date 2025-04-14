import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_133/data.json", "r") as f:
    data = json.load(f)

TotalPainkillerUnits = data["TotalPainkillerUnits"] # scalar parameter
DaytimePainkillerUnits = data["DaytimePainkillerUnits"] # scalar parameter
DaytimeSleepUnits = data["DaytimeSleepUnits"] # scalar parameter
NighttimePainkillerUnits = data["NighttimePainkillerUnits"] # scalar parameter
NighttimeSleepUnits = data["NighttimeSleepUnits"] # scalar parameter
MinimumDaytimePercentage = data["MinimumDaytimePercentage"] # scalar parameter
MinimumNighttimePills = data["MinimumNighttimePills"] # scalar parameter
DaytimePills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DaytimePills")
NighttimePills = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NighttimePills")

# Add constraint to limit total painkiller units used
model.addConstr(
    DaytimePainkillerUnits * DaytimePills + NighttimePainkillerUnits * NighttimePills <= TotalPainkillerUnits,
    name="total_painkiller_limit"
)

# Add constraint to enforce MinimumDaytimePercentage
model.addConstr((1 - MinimumDaytimePercentage) * DaytimePills >= MinimumDaytimePercentage * NighttimePills, name="minimum_daytime_percentage")

# Add constraint to ensure at least MinimumNighttimePills nighttime pills are made
model.addConstr(NighttimePills >= MinimumNighttimePills, name="minimum_nighttime_pills")

# The variable "DaytimePills" is already constrained to be non-negative by default in Gurobi as it is of type CONTINUOUS.

# No additional code is required because the variable "NighttimePills" is non-negative by default (gurobipy non-negative domain for continuous variables).

# Add constraint to ensure total painkiller medicine used does not exceed available amount
model.addConstr(
    DaytimePainkillerUnits * DaytimePills + NighttimePainkillerUnits * NighttimePills <= TotalPainkillerUnits,
    name="painkiller_usage_limit"
)

# Add minimum daytime pills percentage constraint
model.addConstr(
    DaytimePills >= MinimumDaytimePercentage * (DaytimePills + NighttimePills), 
    name="min_daytime_pills_percentage"
)

# Add nighttime pill minimum requirement constraint
model.addConstr(NighttimePills >= MinimumNighttimePills, name="min_nighttime_pills_constraint")

# Set objective
model.setObjective(NighttimeSleepUnits * NighttimePills, gp.GRB.MINIMIZE)

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
