import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_226/data.json", "r") as f:
    data = json.load(f)

CartRate = data["CartRate"] # scalar parameter
CartWorkers = data["CartWorkers"] # scalar parameter
TrolleyRate = data["TrolleyRate"] # scalar parameter
TrolleyWorkers = data["TrolleyWorkers"] # scalar parameter
MinTrolleys = data["MinTrolleys"] # scalar parameter
MaxTrolleyPercentage = data["MaxTrolleyPercentage"] # scalar parameter
DeliveryRate = data["DeliveryRate"] # scalar parameter
NumCarts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumCarts")
NumTrolleys = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumTrolleys")

# No additional code needed since NumCarts is already defined as a non-negative continuous variable

# No additional code needed since the variable "NumTrolleys" is defined with non-negativity by default in Gurobi (continuous variables are automatically non-negative unless specified otherwise).

# Add constraint to ensure at least MinTrolleys trolleys are used
model.addConstr(NumTrolleys >= MinTrolleys, name="min_trolleys_constraint")

# Add constraint to limit transportation by trolleys to MaxTrolleyPercentage  
model.addConstr((1 - MaxTrolleyPercentage) * NumTrolleys * TrolleyRate <= MaxTrolleyPercentage * NumCarts * CartRate, name="trolley_transport_limit")

# Add constraint to ensure combined transportation rate meets or exceeds delivery rate
model.addConstr(CartRate * NumCarts + TrolleyRate * NumTrolleys >= DeliveryRate, name="transportation_rate")

# Add constraint to ensure total transportation rate meets or exceeds required delivery rate
model.addConstr(CartRate * NumCarts + TrolleyRate * NumTrolleys >= DeliveryRate, name="transportation_rate_constraint")

# Add constraint for minimum number of trolleys
model.addConstr(NumTrolleys >= MinTrolleys, name="min_trolleys_constraint")

# Add constraint: The maximum percentage of transportation using trolleys must not exceed the defined threshold
model.addConstr(
    TrolleyRate * NumTrolleys <= MaxTrolleyPercentage * (CartRate * NumCarts + TrolleyRate * NumTrolleys), 
    name="max_trolley_percentage"
)

# Set objective
model.setObjective(CartWorkers * NumCarts + TrolleyWorkers * NumTrolleys, gp.GRB.MINIMIZE)

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
