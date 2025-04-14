import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/AircraftLanding/data.json", "r") as f:
    data = json.load(f)

TotalAircrafts = data["TotalAircrafts"] # scalar parameter
EarliestLandingTime = np.array(data["EarliestLandingTime"]) # ['TotalAircrafts']
LatestLandingTime = np.array(data["LatestLandingTime"]) # ['TotalAircrafts']
TargetLandingTime = np.array(data["TargetLandingTime"]) # ['TotalAircrafts']
PenaltyTimeAfterTarget = np.array(data["PenaltyTimeAfterTarget"]) # ['TotalAircrafts']
PenaltyTimeBeforeTarget = np.array(data["PenaltyTimeBeforeTarget"]) # ['TotalAircrafts']
SeparationTimeMatrix = np.array(data["SeparationTimeMatrix"]) # ['TotalAircrafts', 'TotalAircrafts']
LandingTime = model.addVars(TotalAircrafts, vtype=gp.GRB.CONTINUOUS, name="LandingTime")
SeparationMatrix = model.addVars(TotalAircrafts, TotalAircrafts, vtype=gp.GRB.BINARY, name="SeparationMatrix")
TimeBeforeTarget = model.addVars(TotalAircrafts, vtype=gp.GRB.CONTINUOUS, name="TimeBeforeTarget")
TimeAfterTarget = model.addVars(TotalAircrafts, vtype=gp.GRB.CONTINUOUS, name="TimeAfterTarget")

# Add time window constraints for each aircraft
for i in range(TotalAircrafts):
    model.addConstr(LandingTime[i] >= EarliestLandingTime[i], name="earliest_landing_time_{}".format(i))
    model.addConstr(LandingTime[i] <= LatestLandingTime[i], name="latest_landing_time_{}".format(i))

# Maintain sufficient separation time between consecutive aircraft landings
M = gp.GRB.INFINITY # Large constant M used for big-M constraints

for i in range(TotalAircrafts):
    for j in range(TotalAircrafts):
        if i != j:
            model.addConstr(LandingTime[i] + SeparationTimeMatrix[i, j] <= LandingTime[j] + M * (1 - SeparationMatrix[i,j]), 
                            name=f"separation_time_{i}_{j}_i_before_j")
            model.addConstr(LandingTime[j] + SeparationTimeMatrix[j, i] <= LandingTime[i] + M * SeparationMatrix[i,j], 
                            name=f"separation_time_{i}_{j}_j_before_i")

# TimeBeforeTarget and TimeAfterTarget constraints
for i in range(TotalAircrafts):
    model.addConstr(TimeBeforeTarget[i] >= LandingTime[i] - TargetLandingTime[i], name=f"TimeBeforeTarget_constr_{i}")
    model.addConstr(TimeAfterTarget[i] >= TargetLandingTime[i] - LandingTime[i], name=f"TimeAfterTarget_constr_{i}")

# Non-negativity handled by variable declaration

# Set objective
objective = gp.quicksum((PenaltyTimeBeforeTarget[i] * TimeBeforeTarget[i] +
                         PenaltyTimeAfterTarget[i] * TimeAfterTarget[i])
                        for i in range(TotalAircrafts))
model.setObjective(objective, gp.GRB.MINIMIZE)

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
