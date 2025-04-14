import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_189/data.json", "r") as f:
    data = json.load(f)

TubeCapacity = data["TubeCapacity"] # scalar parameter
TubeCost = data["TubeCost"] # scalar parameter
TankerCapacity = data["TankerCapacity"] # scalar parameter
TankerCost = data["TankerCost"] # scalar parameter
MinVolume = data["MinVolume"] # scalar parameter
Budget = data["Budget"] # scalar parameter
TubeTrailerTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TubeTrailerTrips")
TankerTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TankerTrips")

# No additional code needed since the variable "TubeTrailerTrips" is already defined with non-negativity guaranteed by Gurobi's default behavior for continuous variables (min. bound = 0).

# Since TankerTrips is already defined as a continuous variable, it is inherently non-negative in gurobipy. No additional constraint is required.

# Add constraint for total transported volume
model.addConstr(TubeCapacity * TubeTrailerTrips + TankerCapacity * TankerTrips >= MinVolume, name="min_volume_constraint")

# Add transportation budget constraint
model.addConstr(
    TubeTrailerTrips * TubeCost + TankerTrips * TankerCost <= Budget,
    name="transportation_budget"
)

# Ensure the number of high-pressure tube trailer trips is less than the number of liquefied hydrogen tanker trips
model.addConstr(TubeTrailerTrips <= TankerTrips - 1, name="trailer_tanker_trip_relation")

# Add total hydrogen transport volume constraint
model.addConstr(
    TubeCapacity * TubeTrailerTrips + TankerCapacity * TankerTrips >= MinVolume,
    name="hydrogen_transport_volume"
)

# Add budget constraint
model.addConstr(TubeCost * TubeTrailerTrips + TankerCost * TankerTrips <= Budget, name="budget_constraint")

# Set objective
model.setObjective(TubeTrailerTrips + TankerTrips, gp.GRB.MINIMIZE)

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
