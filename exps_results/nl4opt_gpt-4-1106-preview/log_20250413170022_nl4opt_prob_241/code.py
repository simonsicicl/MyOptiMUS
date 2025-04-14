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
ServersDeliveringByCart = model.addVar(vtype=gp.GRB.INTEGER, name="ServersDeliveringByCart")
ServersDeliveringByHand = model.addVar(vtype=gp.GRB.INTEGER, name="ServersDeliveringByHand")

# Since ServersDeliveringByCart is already guaranteed to be non-negative by its variable type,
# no additional constraint is necessary.
# However, if we needed to explicitly add a constraint, we would do the following:
# model.addConstr(ServersDeliveringByCart >= 0, name="non_negative_servers")

# Since ServersDeliveringByHand is already defined as an integer variable, 
# we just need to add a constraint to ensure it is non-negative.
model.addConstr(ServersDeliveringByHand >= 0, "non_negativity_constraint")



# Ensure that the number of servers delivering by hand meets the minimum requirement
model.addConstr(ServersDeliveringByHand >= MinServersHand, name="min_servers_by_hand")

# Constraint: The total number of customer interactions must meet or exceed TargetInteractions per hour
model.addConstr(ServersDeliveringByCart * InteractionsCart + ServersDeliveringByHand * InteractionsHand >= TargetInteractions, "TotalInteractionsTarget")

# Ensure that the target number of customer interactions is met or exceeded
model.addConstr(ServersDeliveringByCart * InteractionsCart + ServersDeliveringByHand * InteractionsHand >= TargetInteractions, name="target_interactions")

# Ensure the minimum percentage of delivery shifts that must be by cart is respected
model.addConstr(ServersDeliveringByCart >= MinCartShiftsPercentage * (ServersDeliveringByCart + ServersDeliveringByHand), name="min_cart_shifts_constraint")

# Ensure the minimum number of servers delivering by hand is respected
model.addConstr(ServersDeliveringByHand >= MinServersHand, name="min_servers_hand")

# Define the objective function
model.setObjective(ServersDeliveringByCart * RefillsCart + ServersDeliveringByHand * RefillsHand, gp.GRB.MINIMIZE)

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
