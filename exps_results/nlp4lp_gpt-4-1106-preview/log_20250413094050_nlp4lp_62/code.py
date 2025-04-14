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
ProductionBatch = model.addVars(M, P, vtype=gp.GRB.INTEGER, name="ProductionBatch")
TotalProduction = model.addVars(P, vtype=gp.GRB.CONTINUOUS, name="TotalProduction")

# Each machine can be used for up to its availability hours per month
for m in range(M):
    model.addConstr(gp.quicksum(ProductionBatch[m, p] * TimeRequired[m, p] for p in range(P)) <= Availability[m], 
                    name=f"machine_availability_{m}")

# Total production and setup time for all parts on each machine should not exceed available time for that machine
for m in range(len(TimeRequired)):
    for p in range(len(SetupTime)):
        model.addConstr(ProductionBatch[m, p]*TimeRequired[m, p] + SetupTime[p] <= Availability[m], name=f'time_availability_m{m}_p{p}')

# Ensure that each produced batch of any part on any machine is non-negative
for m in range(M):
    for p in range(P):
        model.addConstr(ProductionBatch[m, p] >= 0, name="nonnegativity_constraint_batch_{}_{}".format(m, p))

# Add total production constraints for each part across all machines
for p in range(P):
    model.addConstr(TotalProduction[p] == gp.quicksum(ProductionBatch[m, p] for m in range(M)), name=f"total_production_part_{p}")

# Define the objective function
model.setObjective(
    gp.quicksum(Prices[p] * TotalProduction[p] for p in range(P))
    - gp.quicksum(MachineCosts[m] for m in range(M)),
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
