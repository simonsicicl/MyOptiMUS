import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_183/data.json", "r") as f:
    data = json.load(f)

BalloonCapacity = data["BalloonCapacity"] # scalar parameter
GondolaCapacity = data["GondolaCapacity"] # scalar parameter
BalloonPollution = data["BalloonPollution"] # scalar parameter
GondolaPollution = data["GondolaPollution"] # scalar parameter
MaxBalloons = data["MaxBalloons"] # scalar parameter
MinVisitors = data["MinVisitors"] # scalar parameter
NumberOfBalloons = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBalloons")
NumberOfGondolas = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfGondolas")

# Since NumberOfBalloons has already been defined as an integer variable, 
# we just need to add a constraint to ensure it is non-negative. 
# No need to change its integrality.
model.addConstr(NumberOfBalloons >= 0, "num_balloons_non_negative")

# No code needed as the variable NumberOfGondolas is already defined to be non-negative by its type (INTEGER)

model.addConstr(NumberOfBalloons <= MaxBalloons, name="max_balloons_constraint")

# At least MinVisitors must be transported using hot-air balloons and gondola lifts.
model.addConstr(NumberOfBalloons * BalloonCapacity + NumberOfGondolas * GondolaCapacity >= MinVisitors, "MinVisitors_Transportation")

# Ensure the minimum number of visitors is transported
model.addConstr(NumberOfBalloons * BalloonCapacity + NumberOfGondolas * GondolaCapacity >= MinVisitors, name="min_visitors")

# Add constraint to respect the maximum number of hot air balloon rides available
model.addConstr(NumberOfBalloons <= MaxBalloons, name="max_balloons_constraint")

# Define the objective function
objective = NumberOfBalloons * BalloonPollution + NumberOfGondolas * GondolaPollution

# Set the objective in the model
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
