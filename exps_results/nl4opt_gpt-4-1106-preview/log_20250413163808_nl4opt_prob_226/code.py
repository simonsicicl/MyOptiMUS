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
NumberOfCarts = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCarts")
NumberOfTrolleys = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTrolleys")

model.addConstr(NumberOfCarts >= 0, name="non_negativity_carts")

# Ensure the number of trolleys is non-negative and meets the minimum required
model.addConstr(NumberOfTrolleys >= max(0, MinTrolleys), name="minimum_number_of_trolleys")

# Ensure at least MinTrolleys trolleys are used
model.addConstr(NumberOfTrolleys >= MinTrolleys, name="min_trolleys_constraint")

# Add the constraint for the total rate of transportation performed by trolleys not to exceed MaxTrolleyPercentage of the overall transportation rate.
model.addConstr(NumberOfTrolleys * TrolleyRate <= MaxTrolleyPercentage * (NumberOfCarts * CartRate + NumberOfTrolleys * TrolleyRate), name="max_trolley_transportation_rate")

# Add constraint to ensure transportation rate meets or exceeds delivery rate
model.addConstr((CartRate * NumberOfCarts) + (TrolleyRate * NumberOfTrolleys) >= DeliveryRate, "transportation_rate_requirement")

# Ensure the use of at least the minimum number of trolleys
model.addConstr(NumberOfTrolleys >= MinTrolleys, name="min_trolleys")

# Ensure the total delivery rate meets or exceeds the required delivery rate
model.addConstr(NumberOfCarts * CartRate + NumberOfTrolleys * TrolleyRate >= DeliveryRate, name="delivery_rate_requirement")

# Ensure the maximum percentage of transportation using trolleys is not exceeded
model.addConstr(NumberOfTrolleys * TrolleyRate <= MaxTrolleyPercentage * (NumberOfCarts * CartRate + NumberOfTrolleys * TrolleyRate), name="MaxTrolleyPercentageConstraint")

# Set objective
model.setObjective(NumberOfCarts * CartWorkers + NumberOfTrolleys * TrolleyWorkers, gp.GRB.MINIMIZE)

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
