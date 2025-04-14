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
LampPowers = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="LampPowers")
AbsError = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="AbsError")
ActualIllumination = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="ActualIllumination")

# Add non-negativity constraints for LampPowers
for j in range(M):
    model.addConstr(LampPowers[j] >= 0, name=f"LampPowers_nonneg_{j}")

# Add absolute error constraints
for i in range(N):
    model.addConstr(AbsError[i] >= gp.quicksum(Coefficients[i, j] * LampPowers[j] for j in range(M)) - DesiredIlluminations[i], name=f"abs_error_constraint_pos_{i}")
    model.addConstr(AbsError[i] >= DesiredIlluminations[i] - gp.quicksum(Coefficients[i, j] * LampPowers[j] for j in range(M)), name=f"abs_error_constraint_neg_{i}")

# Add constraints for absolute error being greater than or equal to the negative difference
for i in range(N):
    model.addConstr(AbsError[i] >= DesiredIlluminations[i] - gp.quicksum(Coefficients[i, j] * LampPowers[j] for j in range(M)), 
                    name=f"AbsError_constraint_{i}")

# Add actual illumination constraints
for i in range(N):
    model.addConstr(
        gp.quicksum(Coefficients[i, j] * LampPowers[j] for j in range(M)) == ActualIllumination[i],
        name=f"illumination_constraint_{i}"
    )

# Set objective
model.setObjective(gp.quicksum(AbsError[i] for i in range(N)), gp.GRB.MINIMIZE)

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
