import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/52/data.json", "r") as f:
    data = json.load(f)

M = data["M"] # scalar parameter
P = data["P"] # scalar parameter
TimeRequired = np.array(data["TimeRequired"]) # ['M', 'P']
MachineCosts = np.array(data["MachineCosts"]) # ['M']
Availability = np.array(data["Availability"]) # ['M']
Prices = np.array(data["Prices"]) # ['P']
MinBatches = np.array(data["MinBatches"]) # ['P']
BatchesProduced = model.addVars(P, vtype=gp.GRB.CONTINUOUS, name="BatchesProduced")

# Ensure that each part has a non-negative number of batches produced
for p in range(P):
    model.addConstr(BatchesProduced[p] >= 0, name="non_negativity_batches_produced_{}".format(p))

# Add machine availability constraints for each machine m
for m in range(M):
    model.addConstr(gp.quicksum(TimeRequired[m,p] * BatchesProduced[p] for p in range(P)) <= Availability[m], name=f"machine_availability_{m}")

P = range(len(MinBatches))
BatchesProduced = model.addVars(P, vtype=gp.GRB.CONTINUOUS, name='BatchesProduced')

# Define dimensions based on TimeRequired shape
M, P = TimeRequired.shape

# Add constraints for total time used on each machine by all parts
for m in range(M):
    model.addConstr(Availability[m] >= gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(P)), name=f"machine_time_usage_{m}")

# Define the objective function
objective = gp.quicksum(Prices[p] * BatchesProduced[p] for p in range(P)) \
            - gp.quicksum(MachineCosts[m] * gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(P)) for m in range(M))

# Set the model to maximize the objective
model.setObjective(objective, gp.GRB.MAXIMIZE)

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
