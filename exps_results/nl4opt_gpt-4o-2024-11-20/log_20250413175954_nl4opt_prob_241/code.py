import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_241/data.json", "r") as f:
    data = json.load(f)

InteractionsCart = data["InteractionsCart"] # scalar parameter
RefillsCart = data["RefillsCart"] # scalar parameter
InteractionsHand = data["InteractionsHand"] # scalar parameter
RefillsHand = data["RefillsHand"] # scalar parameter
MinCartShiftsPercentage = data["MinCartShiftsPercentage"] # scalar parameter
MinServersHand = data["MinServersHand"] # scalar parameter
TargetInteractions = data["TargetInteractions"] # scalar parameter
ServersCart = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServersCart")
ServersHand = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServersHand")

# The non-negativity constraint is implicitly satisfied as ServersCart is a continuous variable which is non-negative by default in Gurobi. Hence, no additional code is required.

# Add non-negativity constraint for ServersHand
model.addConstr(ServersHand >= 0, name="non_negative_ServersHand")

# Add constraint ensuring at least MinCartShiftsPercentage of delivery shifts are by cart
model.addConstr((1 - MinCartShiftsPercentage) * ServersCart >= MinCartShiftsPercentage * ServersHand, name="min_cart_shifts_percentage")

# Add constraint to ensure at least the minimum number of servers are delivering by hand
model.addConstr(ServersHand >= MinServersHand, name="min_servers_hand_constraint")

# Add constraint to ensure total customer interactions meet or exceed the target
model.addConstr(
    ServersCart * InteractionsCart + ServersHand * InteractionsHand >= TargetInteractions,
    name="customer_interactions_target"
)

# Add constraint to ensure total customer interactions meet or exceed the target
model.addConstr(
    ServersCart * InteractionsCart + ServersHand * InteractionsHand >= TargetInteractions,
    name="total_customer_interactions_target"
)

# Add constraint to ensure minimum percentage of total delivery shifts are done by cart
model.addConstr(ServersCart >= MinCartShiftsPercentage * (ServersCart + ServersHand), name="min_cart_shifts_percentage")

# Add constraint for minimum number of servers using hand delivery
model.addConstr(ServersHand >= MinServersHand, name="min_servers_hand_delivery")

# Set objective
model.setObjective(ServersCart * RefillsCart + ServersHand * RefillsHand, gp.GRB.MINIMIZE)

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
