import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/55/data.json", "r") as f:
    data = json.load(f)

P = data["P"] # scalar parameter
C = data["C"] # scalar parameter
Supply = np.array(data["Supply"]) # ['P']
Demand = np.array(data["Demand"]) # ['C']
TransmissionCosts = np.array(data["TransmissionCosts"]) # ['P', 'C']
ElectricitySupplied = model.addVars(P, C, vtype=gp.GRB.CONTINUOUS, name="ElectricitySupplied")

# Add supply capacity constraints for each power plant
for p in range(P):
    model.addConstr(gp.quicksum(ElectricitySupplied[p, c] for c in range(C)) <= Supply[p], name=f"supply_capacity_{p}")

# Ensure each city receives its specific electricity demand
for c in range(C):
    model.addConstr(gp.quicksum(ElectricitySupplied[p, c] for p in range(P)) == Demand[c], name=f"demand_constraint_city_{c}")

# Demand satisfaction constraints for each city
for c in range(C):
    model.addConstr(gp.quicksum(ElectricitySupplied[p, c] for p in range(P)) >= Demand[c], name=f"Demand_satisfaction_city_{c}")

# Power plants cannot send more electricity than their supply capacity to cities
for p in range(P):
    model.addConstr(gp.quicksum(ElectricitySupplied[p, c] for c in range(C)) <= Supply[p], name=f"supply_capacity_{p}")

# Fixed code
ElectricitySupplied = model.addVars(P, C, vtype=gp.GRB.CONTINUOUS, name="ElectricitySupplied")

# Set objective
model.setObjective(gp.quicksum(TransmissionCosts[p, c] * ElectricitySupplied[p, c] for p in range(P) for c in range(C)), gp.GRB.MINIMIZE)

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
