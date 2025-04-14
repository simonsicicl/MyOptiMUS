import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/47/data.json", "r") as f:
    data = json.load(f)

P = data["P"] # scalar parameter
M = data["M"] # scalar parameter
TimeRequired = np.array(data["TimeRequired"]) # ['M', 'P']
MachineCosts = np.array(data["MachineCosts"]) # ['M']
Availability = np.array(data["Availability"]) # ['M']
Prices = np.array(data["Prices"]) # ['P']
MinBatches = np.array(data["MinBatches"]) # ['P']
Batches = model.addVars(P, vtype=gp.GRB.CONTINUOUS, name="Batches")

# Constraint to ensure the number of batches produced for each part is non-negative
for p in range(P):
    model.addConstr(Batches[p] >= 0, name=f"non_negativity_batches_{p}")

# Add machine availability constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * Batches[p] for p in range(P)) <= Availability[m],
        name=f"machine_availability_{m}"
    )

# Add constraints to ensure at least MinBatches for each part p are produced
for p in range(P):
    model.addConstr(Batches[p] >= MinBatches[p], name=f"min_batches_part_{p}")

# Add machine time availability constraints
for m in range(M):
    model.addConstr(gp.quicksum(TimeRequired[m, p] * Batches[p] for p in range(P)) <= Availability[m], name=f"time_availability_machine_{m}")

# Add minimum production constraints
for p in range(P):
    model.addConstr(Batches[p] >= MinBatches[p], name=f"min_production_req_{p}")

# Set objective
model.setObjective(gp.quicksum(Prices[p] * Batches[p] for p in range(P)) - gp.quicksum(MachineCosts[m] for m in range(M)), gp.GRB.MAXIMIZE)

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
