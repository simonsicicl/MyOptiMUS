import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/62/data.json", "r") as f:
    data = json.load(f)

M = data["M"] # scalar parameter
P = data["P"] # scalar parameter
TimeRequired = np.array(data["TimeRequired"]) # ['M', 'P']
MachineCosts = np.array(data["MachineCosts"]) # ['M']
Availability = np.array(data["Availability"]) # ['M']
Prices = np.array(data["Prices"]) # ['P']
SetupTime = np.array(data["SetupTime"]) # ['P']
BatchProduced = model.addVars(M, P, vtype=gp.GRB.INTEGER, name="BatchProduced")

# Add machine usage constraints
for m in range(M):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchProduced[m, p] for p in range(P)) <= Availability[m],
        name=f"machine_usage_{m}"
    )

# Add constraints to ensure that total production time on each machine does not exceed available time
for m in range(M):
    model.addConstr(
        gp.quicksum(
            BatchProduced[m, p] * TimeRequired[m, p] + SetupTime[p] * BatchProduced[m, p]
            for p in range(P)
        ) <= Availability[m],
        name=f"production_time_limit_machine_{m}"
    )

# Non-negativity constraint for the number of batches
for m in range(M):
    for p in range(P):
        model.addConstr(BatchProduced[m, p] >= 0, name=f"non_negativity_batches_m{m}_p{p}")

# Add constraints to ensure total time used (batch production + setup time) does not exceed machine availability
for m in range(M):
    model.addConstr(
        gp.quicksum(
            TimeRequired[m, p] * BatchProduced[m, p] + SetupTime[p] * BatchProduced[m, p]
            for p in range(P)
        ) <= Availability[m],
        name=f"machine_time_constraint_{m}"
    )

# Set objective
model.setObjective(gp.quicksum(BatchProduced[m, p] * Prices[p] for m in range(M) for p in range(P)) - gp.quicksum(MachineCosts[m] for m in range(M)), gp.GRB.MAXIMIZE)

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
