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
Deviation = model.addVars(NumObs, vtype=gp.GRB.CONTINUOUS, lb=0.0, name="Deviation")
Slope = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Slope")
Intercept = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Intercept")
MaxDeviation = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MaxDeviation")

# Add a constraint for the maximum deviation among all predicted and observed y values
maxDeviation = model.addVar(vtype=gp.GRB.CONTINUOUS, name="maxDeviation")
model.update()  # Integrate new variable
for i in range(NumObs):
    model.addConstr(Deviation[i] <= maxDeviation, name=f"max_deviation_constr_{i}")
model.setObjective(maxDeviation, gp.GRB.MINIMIZE)

# Since we aim to minimize the maximum deviation, we need an auxiliary variable to represent this maximum deviation
maxDeviation = model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0.0, name="maxDeviation")

# Add constraints to ensure that the maxDeviation variable is greater than or equal to all Deviation variables
for k in range(NumObs):
    model.addConstr(maxDeviation >= Deviation[k], name=f"max_deviation_constraint_{k}")

# Set the objective to minimize the maximum deviation
model.setObjective(maxDeviation, gp.GRB.MINIMIZE)

# Add deviation constraints
for i in range(NumObs):
    model.addConstr(Deviation[i] >= Y[i] - (Slope * X[i] + Intercept), name=f"deviation_constr_{i}")

# Add constraints for deviation being greater than or equal to the negative difference between observed and predicted y values
for i in range(NumObs):
    model.addConstr(Deviation[i] >= -(Y[i] - (Slope * X[i] + Intercept)), name=f"deviation_constr_{i}")

Deviation = model.addVars(NumObs, vtype=gp.GRB.CONTINUOUS, lb=0.0, name='Deviation')
Slope = model.addVar(vtype=gp.GRB.CONTINUOUS, name='Slope')
Intercept = model.addVar(vtype=gp.GRB.CONTINUOUS, name='Intercept')

# Add deviation constraints
for k in range(NumObs):
    model.addConstr(Deviation[k] >= -(Slope * X[k] + Intercept - Y[k]), name=f"deviation_constr_{k}")

# Absolute value constraints via auxiliary variables and constraints
for i in range(NumObs):
    Deviation = model.addVar(vtype=gp.GRB.CONTINUOUS, name=f"Deviation_{i}")
    model.addConstr(Deviation == Y[i] - (Slope * X[i] + Intercept), name=f"deviation_{i}")
    model.addGenConstrAbs(MaxDeviation, Deviation, name=f"genconstr_abs_{i}")

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
