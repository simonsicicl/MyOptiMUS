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
b = model.addVar(vtype=gp.GRB.CONTINUOUS, name="b")
a = model.addVar(vtype=gp.GRB.CONTINUOUS, name="a")
Dev = model.addVars(K, vtype=gp.GRB.CONTINUOUS, name="Dev")

# Add constraints to relate absolute deviation `Dev_k` to the positive deviation of `Y_k` from the predicted value `(b * X_k + a)`
for k in range(K):
    model.addConstr(Dev[k] >= Y[k] - (b * X[k] + a), name=f"absolute_dev_relation_{k}")

# Relate absolute deviation to negative deviation constraints
for k in range(K):
    model.addConstr(Dev[k] >= -(Y[k] - (b * X[k] + a)), name=f"abs_dev_constraint_{k}")

# Set objective
model.setObjective(gp.quicksum(Dev[k] for k in range(K)), gp.GRB.MINIMIZE)

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
