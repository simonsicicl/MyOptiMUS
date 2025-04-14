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
DeliveriesByCanoe = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DeliveriesByCanoe")
TotalDeliveries = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalDeliveries")
DeliveriesByRunner = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DeliveriesByRunner")
TotalTime = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalTime")
RunnersUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RunnersUsed")
CanoersUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CanoersUsed")
CanoeProportion = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CanoeProportion")

# Add constraint: At most MaxCanoeProportion of deliveries can be by canoe
model.addConstr(DeliveriesByCanoe <= MaxCanoeProportion * TotalDeliveries, name="canoe_delivery_proportion")

# Add constraint ensuring the total delivery time doesn't exceed the total available hours
model.addConstr(TotalTime <= TotalHours, name="total_time_constraint")

# Add constraint for minimum number of deliveries by runners
model.addConstr(DeliveriesByRunner >= MinRunners, name="min_runners_constraint")

# No additional code is required because the variable "RunnersUsed" is already non-negative due to its default lower bound (0) in Gurobi.

# The non-negativity of CanoersUsed is automatically ensured due to its default non-negative domain as a continuous variable,
# so no constraint code is required.

# Add constraint ensuring TotalDeliveries is the sum of deliveries by canoers and runners
model.addConstr(TotalDeliveries == DeliveriesByCanoe + DeliveriesByRunner, name="total_deliveries_constraint")

# Add constraint defining TotalTime as the sum of time contributions by runners and canoers
model.addConstr(TotalTime == DeliveriesByRunner * TimePerRunner + DeliveriesByCanoe * TimePerCanoer, name="TotalTime_constraint")

# Add constraint to ensure total deliveries equals the sum of deliveries by runners and canoers
model.addConstr(TotalDeliveries == DeliveriesByRunner + DeliveriesByCanoe, name="total_deliveries_constraint")

# Add constraint to ensure total delivery times do not exceed available hours
model.addConstr(
    (DeliveriesByRunner * TimePerRunner) + (DeliveriesByCanoe * TimePerCanoer) <= TotalHours,
    name="total_time_constraint"
)

# Add constraint to ensure CanoeProportion is less than or equal to MaxCanoeProportion
model.addConstr(CanoeProportion <= MaxCanoeProportion, name="canoe_proportion_limit")

# Add proportion constraint for deliveries by canoers
model.addConstr(CanoeProportion * TotalDeliveries == DeliveriesByCanoe, name="canoe_proportion_constraint")

# Add constraint ensuring the minimum number of runners is used
model.addConstr(RunnersUsed >= MinRunners, name="min_runners_constraint")

# Set objective
model.setObjective((DeliveriesByRunner * BagsPerRunner) + (DeliveriesByCanoe * BagsPerCanoer), gp.GRB.MAXIMIZE)

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
