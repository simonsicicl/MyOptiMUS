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
BatchesOfPart = model.addVars(P, vtype=gp.GRB.INTEGER, name="BatchesOfPart")
TotalMachineTimeUsed = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="TotalMachineTimeUsed")

# Ensure non-negative production constraints for each part
for p in range(P):
    model.addConstr(BatchesOfPart[p] >= 0, name="non_negative_batches_p" + str(p))

# Add machine availability constraints
for m in range(M):
    model.addConstr(gp.quicksum(TimeRequired[m,p] * BatchesOfPart[p] for p in range(P)) <= Availability[m], name=f"machine_availability_{m}")

# Ensure each part is produced in at least MinBatches quantity
for p in range(P):
    model.addConstr(BatchesOfPart[p] >= MinBatches[p], name=f"min_batches_part_{p}")

# Total machine time used must equal the sum of time required for all parts on that machine
for m in range(M):
    model.addConstr(TotalMachineTimeUsed[m] == gp.quicksum(TimeRequired[m, p] * BatchesOfPart[p] for p in range(P)), name=f"TotalMachineTime_m{m}")

# Set objective
model.setObjective(
    gp.quicksum(Prices[p] * BatchesOfPart[p] for p in range(P))
    - gp.quicksum(MachineCosts[m] * TotalMachineTimeUsed[m] for m in range(M)),
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
