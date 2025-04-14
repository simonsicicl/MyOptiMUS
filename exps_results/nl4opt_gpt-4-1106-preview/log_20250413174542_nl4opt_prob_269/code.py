import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_269/data.json", "r") as f:
    data = json.load(f)

BagsPerRunner = data["BagsPerRunner"] # scalar parameter
TimePerRunner = data["TimePerRunner"] # scalar parameter
BagsPerCanoer = data["BagsPerCanoer"] # scalar parameter
TimePerCanoer = data["TimePerCanoer"] # scalar parameter
MaxCanoeProportion = data["MaxCanoeProportion"] # scalar parameter
TotalHours = data["TotalHours"] # scalar parameter
MinRunners = data["MinRunners"] # scalar parameter
TotalBagsDeliveredByCanoer = model.addVar(vtype=gp.GRB.INTEGER, name="TotalBagsDeliveredByCanoer")
TotalBagsDelivered = model.addVar(vtype=gp.GRB.INTEGER, name="TotalBagsDelivered")
NumberOfRunners = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfRunners")
NumberOfCanoers = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCanoers")

# At most MaxCanoeProportion of deliveries can be by canoe
model.addConstr(TotalBagsDeliveredByCanoer <= MaxCanoeProportion * TotalBagsDelivered, name="canoe_proportion_constraint")

# Define the total delivery time constraint
model.addConstr(
    (TotalBagsDeliveredByCanoer / BagsPerCanoer) * TimePerCanoer +
    ((TotalBagsDelivered - TotalBagsDeliveredByCanoer) / BagsPerRunner) * TimePerRunner
    <= TotalHours,
    name="total_delivery_time"
)

# At least MinRunners must be involved in the delivery
model.addConstr(TotalBagsDelivered - TotalBagsDeliveredByCanoer >= MinRunners * BagsPerRunner, name="min_runners_involved")

# Add constraint to ensure the number of runners used is non-negative
model.addConstr(NumberOfRunners >= 0, name="NumberOfRunners_non_negative")

# Add non-negativity constraint for the number of canoers used
model.addConstr(NumberOfCanoers >= 0, name="non_negativity_canoers")

# Relate total bags delivered by canoers to the number of canoers and bags each canoer can carry
model.addConstr(TotalBagsDeliveredByCanoer == BagsPerCanoer * NumberOfCanoers, name="total_bags_delivered_by_canoer")

# Total number of bags delivered is the sum of bags delivered by runners and canoers
TotalBagsDelivered = model.addVar(vtype=gp.GRB.INTEGER, name="TotalBagsDelivered")
model.addConstr(TotalBagsDelivered == TotalBagsDeliveredByCanoer + NumberOfRunners * BagsPerRunner, name="total_bags_delivered_constraint")

# Ensure that the maximum proportion of deliveries done by canoe is not exceeded
model.addConstr(TotalBagsDeliveredByCanoer <= MaxCanoeProportion * TotalBagsDelivered, name="max_canoe_proportion_constraint")

# Ensure the total hours used by both runners and canoers does not exceed the total available delivery hours
model.addConstr(NumberOfRunners * TimePerRunner + NumberOfCanoers * TimePerCanoer <= TotalHours, "total_hours_constraint")

# Ensure the minimum number of runners is used
model.addConstr(NumberOfRunners >= MinRunners, name="min_runners_constraint")

# Set objective
model.setObjective(TotalBagsDelivered, gp.GRB.MAXIMIZE)

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
