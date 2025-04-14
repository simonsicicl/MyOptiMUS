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
NumberOfTubeTrailersUsed = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTubeTrailersUsed")
NumberOfTankersUsed = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTankersUsed")

# Since the variable NumberOfTubeTrailersUsed is already declared as non-negative by default (all variables are non-negative unless otherwise specified), there is no need to add an additional constraint.
# Non-negativity is guaranteed by the variable type (INTEGER).

# Since NumberOfTankersUsed is already an integer variable, we just need to add a constraint ensuring it's non-negative
model.addConstr(NumberOfTankersUsed >= 0, name="non_negative_tankers")

# Add constraint for the minimum total transported volume
model.addConstr(NumberOfTubeTrailersUsed * TubeCapacity + NumberOfTankersUsed * TankerCapacity >= MinVolume, name="min_transport_volume")

# Add total cost constraint
total_cost = NumberOfTubeTrailersUsed * TubeCost + NumberOfTankersUsed * TankerCost
model.addConstr(total_cost <= Budget, name="budget_constraint")

# Add constraint to ensure the number of high-pressure tube trailer trips 
# is less than the number of liquefied hydrogen tanker trips
model.addConstr(NumberOfTubeTrailersUsed <= NumberOfTankersUsed, name="tube_trailer_vs_tanker_trips")

# Ensure the minimum total volume of hydrogen is transported
model.addConstr(NumberOfTubeTrailersUsed * TubeCapacity + NumberOfTankersUsed * TankerCapacity >= MinVolume, name="min_hydrogen_volume_constraint")

# Ensure the cost of transportation does not exceed the budget
model.addConstr(NumberOfTubeTrailersUsed * TubeCost + NumberOfTankersUsed * TankerCost <= Budget, name="budget_constraint")

# Set objective
model.setObjective(NumberOfTubeTrailersUsed + NumberOfTankersUsed, gp.GRB.MINIMIZE)

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
