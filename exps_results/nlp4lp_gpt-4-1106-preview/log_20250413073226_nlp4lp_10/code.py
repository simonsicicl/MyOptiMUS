import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/10/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
M = data["M"] # scalar parameter
Coefficients = np.array(data["Coefficients"]) # ['N', 'M']
DesiredIlluminations = np.array(data["DesiredIlluminations"]) # ['N']
LampPower = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="LampPower")
PositiveDeviation = model.addVars(N, vtype=gp.GRB.CONTINUOUS, lb=0.0, name="PositiveDeviation")
NegativeDeviation = model.addVars(N, vtype=gp.GRB.CONTINUOUS, lb=0.0, name="NegativeDeviation")

# Ensure lamp power values are non-negative
for j in range(M):
    model.addConstr(LampPower[j] >= 0, name=f"LampPower_nonneg_{j}")

# Actual illumination at point i constraints
for i in range(N):
    model.addConstr(PositiveDeviation[i] - NegativeDeviation[i] == gp.quicksum(Coefficients[i, j] * LampPower[j] for j in range(M)) - DesiredIlluminations[i], name="illumination_balance")

# Since PositiveDeviation and NegativeDeviation are already non-negative by their definition, no additional constraints are needed.

# Define objective function
model.setObjective(gp.quicksum(PositiveDeviation[i] + NegativeDeviation[i] for i in range(N)), gp.GRB.MINIMIZE)

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
