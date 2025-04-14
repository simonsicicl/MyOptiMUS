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
NumberOfTrains = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTrains")
NumberOfTrams = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTrams")

# The number of trains must be non-negative. Since the variable is defined as an integer, it cannot be negative by definition in Gurobi.
# No additional constraint is needed.

model.addConstr(NumberOfTrams >= 0, name="trams_non_negative")

# Add the constraint that number of trams must be at least TramTrainRatio times the number of trains
model.addConstr(NumberOfTrams >= TramTrainRatio * NumberOfTrains, name="TramTrainRatioConstraint")

# Constraint: Total transportation capacity should meet or exceed the minimum required people per hour
model.addConstr((NumberOfTrains * TrainCapacity) + (NumberOfTrams * TramCapacity) >= MinPeople, "capacity_constraint")

TrainCapacity = data["TrainCapacity"]  # scalar parameter, assumed to be defined as given
TramCapacity = data["TramCapacity"]    # scalar parameter, assumed to be defined as given
MinPeople = data["MinPeople"]          # scalar parameter, assumed to be defined as given

# Ensure that the minimum number of people per hour to be transported is met
model.addConstr(TrainCapacity * NumberOfTrains + TramCapacity * NumberOfTrams >= MinPeople, name="min_people_transportation")

# Add constraint to ensure that the number of trams is at least twice the number of trains
model.addConstr(NumberOfTrams >= TramTrainRatio * NumberOfTrains, name="TramTrainMinRatio")

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
