import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/31/data.json", "r") as f:
    data = json.load(f)

K = data["K"] # scalar parameter
Y = np.array(data["Y"]) # ['K']
X = np.array(data["X"]) # ['K']
DeviationPlus = model.addVars(K, vtype=gp.GRB.CONTINUOUS, name="DeviationPlus")
DeviationMinus = model.addVars(K, vtype=gp.GRB.CONTINUOUS, name="DeviationMinus")

a = model.addVar(vtype=gp.GRB.CONTINUOUS, name='a')
b = model.addVar(vtype=gp.GRB.CONTINUOUS, name='b')

# Ensure deviations capture the absolute difference between observed and predicted Y values
for k in range(K):
    model.addConstr(DeviationPlus[k] - DeviationMinus[k] == Y[k] - (b * X[k] + a), name=f'deviation_abs_{k}')

# Non-negativity constraint for DeviationPlus
for k in range(K):
    model.addConstr(DeviationPlus[k] >= 0, name=f"nonnegativity_devplus_{k}")

# Non-negativity constraint for DeviationMinus
for k in range(K):
    model.addConstr(DeviationMinus[k] >= 0, name=f"DeviationMinus_nonneg_{k}")

# Set objective
model.setObjective(gp.quicksum(DeviationPlus[k] + DeviationMinus[k] for k in range(K)), gp.GRB.MINIMIZE)

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
