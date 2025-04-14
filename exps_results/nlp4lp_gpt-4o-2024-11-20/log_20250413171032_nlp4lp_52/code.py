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
MachineTimeUsed = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="MachineTimeUsed")

# Add non-negativity constraint for BatchesProduced
for p in range(P):
    model.addConstr(BatchesProduced[p] >= 0, name=f"non_negative_batches_{p}")

# Add machine availability constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(P)) <= Availability[m],
        name=f"machine_availability_{m}"
    )

# Add constraints to ensure each part p is produced in at least MinBatches[p] batches
for p in range(P):
    model.addConstr(BatchesProduced[p] >= MinBatches[p], name=f"min_batches_part_{p}")

# Add machine time availability constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(P)) <= Availability[m],
        name=f"machine_availability_{m}"
    )

# Add constraints to calculate the total time each machine is used
for m in range(M):
    model.addConstr(
        MachineTimeUsed[m] == gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(P)), 
        name=f"machine_time_used_{m}"
    )

# Add machine usage constraints
for m in range(M):
    model.addConstr(MachineTimeUsed[m] <= Availability[m], name=f"machine_availability_{m}")

# Add minimum production constraints
for p in range(P):
    model.addConstr(BatchesProduced[p] >= MinBatches[p], name=f"min_production_{p}")

# Set objective
model.setObjective(
    gp.quicksum(Prices[p] * BatchesProduced[p] for p in range(P)) - 
    gp.quicksum(MachineCosts[m] * MachineTimeUsed[m] for m in range(M)),
    gp.GRB.MAXIMIZE
)

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
