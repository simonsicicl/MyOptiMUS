import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/6/data.json", "r") as f:
    data = json.load(f)

InitialPosition = data["InitialPosition"] # scalar parameter
InitialVelocity = data["InitialVelocity"] # scalar parameter
FinalPosition = data["FinalPosition"] # scalar parameter
FinalVelocity = data["FinalVelocity"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
Acceleration = model.addVars(TotalTime, vtype=gp.GRB.CONTINUOUS, name="Acceleration")
AbsAcceleration = model.addVars(TotalTime, vtype=gp.GRB.CONTINUOUS, name="AbsAcceleration")

# Add constraints to ensure AbsAcceleration is the absolute value of Acceleration
for t in range(TotalTime):
    model.addConstr(AbsAcceleration[t] >= Acceleration[t], name=f"abs_acceleration_pos_{t}")
    model.addConstr(AbsAcceleration[t] >= -Acceleration[t], name=f"abs_acceleration_neg_{t}")

# Add constraints to define AbsAcceleration as the absolute value of Acceleration (negative case)
for t in range(TotalTime):
    model.addConstr(AbsAcceleration[t] >= -Acceleration[t], name=f"abs_accel_neg_{t}")

# Set objective
model.setObjective(gp.quicksum(AbsAcceleration[t] for t in range(TotalTime)), gp.GRB.MINIMIZE)

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
