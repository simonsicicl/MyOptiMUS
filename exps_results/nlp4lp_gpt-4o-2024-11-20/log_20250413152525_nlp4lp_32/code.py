import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/32/data.json", "r") as f:
    data = json.load(f)

NumObs = data["NumObs"] # scalar parameter
Y = np.array(data["Y"]) # ['NumObs']
X = np.array(data["X"]) # ['NumObs']
AbsDeviation = model.addVars(NumObs, vtype=gp.GRB.CONTINUOUS, name="AbsDeviation")
YPred = model.addVars(NumObs, vtype=gp.GRB.CONTINUOUS, name="YPred")
MaxDeviation = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MaxDeviation")
a = model.addVar(vtype=gp.GRB.CONTINUOUS, name="a")
b = model.addVar(vtype=gp.GRB.CONTINUOUS, name="b")
AbsDeviation = model.addVars(NumObs, vtype=gp.GRB.CONTINUOUS, name="AbsDeviation")
MaxDeviation = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MaxDeviation")

# Add constraints for defining YPred values
for i in range(NumObs):
    model.addConstr(YPred[i] == a * X[i] + b, name=f"ypred_def_{i}")

# Add constraints for AbsDeviation lower bounds
for i in range(NumObs):
    model.addConstr(AbsDeviation[i] >= YPred[i] - Y[i], name=f"abs_dev_pos_{i}")
    model.addConstr(AbsDeviation[i] >= Y[i] - YPred[i], name=f"abs_dev_neg_{i}")

# Add constraints for MaxDeviation
for i in range(NumObs):
    model.addConstr(MaxDeviation >= AbsDeviation[i], name=f"max_dev_{i}")

# Add constraints to minimize the maximum absolute deviation across all points
for i in range(len(Y)):  # Assuming Y and YPred are lists or arrays of the same length
    model.addConstr(Y[i] - YPred[i] <= MaxDeviation, name=f"deviation_upper_bound_{i}")
    model.addConstr(YPred[i] - Y[i] <= MaxDeviation, name=f"deviation_lower_bound_{i}")

# Add absolute deviation constraints
for k in range(NumObs):
    model.addConstr(AbsDeviation[k] >= Y[k] - YPred[k], name=f"abs_dev_pos_diff_{k}")
    model.addConstr(AbsDeviation[k] >= YPred[k] - Y[k], name=f"abs_dev_neg_diff_{k}")

# Add constraints to ensure MaxDeviation is greater than or equal to the absolute deviation for all points
for k in range(NumObs):
    model.addConstr(MaxDeviation >= AbsDeviation[k], name=f"max_deviation_constraint_{k}")

# Add linear relationship constraints between YPred_k and X_k
for k in range(NumObs):
    model.addConstr(YPred[k] == a * X[k] + b, name=f"linear_relationship_{k}")

# Add constraints to define the predicted y values based on the linear model
for i in range(NumObs):
    model.addConstr(YPred[i] == a * X[i] + b, name=f"linear_model_constraint_{i}")

# Add absolute deviation constraints
for i in range(NumObs):
    model.addConstr(AbsDeviation[i] >= Y[i] - YPred[i], name=f"abs_deviation_{i}")

# Add absolute deviation constraints
for i in range(NumObs):
    model.addConstr(AbsDeviation[i] >= YPred[i] - Y[i], name=f"AbsDeviation_constraint_{i}")

# Add maximum absolute deviation constraint
for i in range(NumObs):
    model.addConstr(MaxDeviation >= AbsDeviation[i], name=f"max_abs_deviation_{i}")

# Set objective
model.setObjective(MaxDeviation, gp.GRB.MINIMIZE)

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
