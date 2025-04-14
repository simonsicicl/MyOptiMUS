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
DaytimePillsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DaytimePillsProduced")
NighttimePillsProduced = model.addVar(vtype=gp.GRB.INTEGER, name="NighttimePillsProduced")

# Total units of painkiller medicine used cannot exceed TotalPainkillerUnits constraint
model.addConstr(DaytimePainkillerUnits * DaytimePillsProduced + NighttimePainkillerUnits * NighttimePillsProduced <= TotalPainkillerUnits, "TotalPainkillerConstraint")

# Constraint: At least MinimumDaytimePercentage of the total number of pills must be daytime pills
DaytimePillsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DaytimePillsProduced")
NighttimePillsProduced = model.addVar(vtype=gp.GRB.INTEGER, name="NighttimePillsProduced")
MinimumDaytimePercentage = data["MinimumDaytimePercentage"]  # scalar parameter

model.addConstr((DaytimePillsProduced >= MinimumDaytimePercentage * (DaytimePillsProduced + NighttimePillsProduced)),
                name="MinDaytimePills")

# At least MinimumNighttimePills nighttime pills must be made
model.addConstr(NighttimePillsProduced >= MinimumNighttimePills, name="min_nighttime_pills")

# Add constraint to ensure the number of daytime pills produced is non-negative
model.addConstr(DaytimePillsProduced >= 0, name="non_negative_daytime_pills")

# Add constraint to ensure that the number of nighttime pills produced is non-negative
NighttimePillsProduced.setAttr(gp.GRB.Attr.LB, 0.0)

# Ensure that at least the minimum percentage of pills are daytime pills
DaytimePillsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DaytimePillsProduced")
NighttimePillsProduced = model.addVar(vtype=gp.GRB.INTEGER, name="NighttimePillsProduced")
MinimumDaytimePercentage = data["MinimumDaytimePercentage"] # scalar parameter

model.addConstr(DaytimePillsProduced >= MinimumDaytimePercentage * (DaytimePillsProduced + NighttimePillsProduced), name="min_daytime_pills")

# Ensure that at least the minimum number of nighttime pills are produced
model.addConstr(NighttimePillsProduced >= MinimumNighttimePills, name="min_nighttime_pills")

# Ensure that the total use of painkiller medicine does not exceed the available units
model.addConstr((DaytimePillsProduced * DaytimePainkillerUnits) + (NighttimePillsProduced * NighttimePainkillerUnits) <= TotalPainkillerUnits, "painkiller_usage")

# Set objective
model.setObjective(DaytimePillsProduced * DaytimeSleepUnits + NighttimePillsProduced * NighttimeSleepUnits, gp.GRB.MINIMIZE)

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
