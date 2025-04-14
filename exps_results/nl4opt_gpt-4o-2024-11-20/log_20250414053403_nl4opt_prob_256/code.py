import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_256/data.json", "r") as f:
    data = json.load(f)

TrainCapacity = data["TrainCapacity"] # scalar parameter
TramCapacity = data["TramCapacity"] # scalar parameter
TramTrainRatio = data["TramTrainRatio"] # scalar parameter
MinPeople = data["MinPeople"] # scalar parameter
NumberOfTrains = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfTrains")
NumberOfTrams = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfTrams")

# The constraint is already satisfied as non-negativity is automatically enforced for continuous variables in Gurobi.

# The variable "NumberOfTrams" is non-negative due to its default lower bound (0) in Gurobi.

# Add constraint for tram to train ratio
model.addConstr(NumberOfTrams >= TramTrainRatio * NumberOfTrains, name="tram_train_ratio")

# Add capacity constraint for trains and trams
model.addConstr(NumberOfTrains * TrainCapacity + NumberOfTrams * TramCapacity >= MinPeople, name="capacity_constraint")

# Add transportation capacity constraint
model.addConstr(NumberOfTrains * TrainCapacity + NumberOfTrams * TramCapacity >= MinPeople, name="transportation_capacity")

# Enforce the minimum ratio of the number of trams to the number of trains
model.addConstr(NumberOfTrams >= TramTrainRatio * NumberOfTrains, name="min_tram_train_ratio")

# Set objective
model.setObjective(NumberOfTrains + NumberOfTrams, gp.GRB.MINIMIZE)

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
