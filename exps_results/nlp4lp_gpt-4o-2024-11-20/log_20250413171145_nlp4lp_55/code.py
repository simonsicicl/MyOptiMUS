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
ElectricityTransferred = model.addVars(P, C, vtype=gp.GRB.CONTINUOUS, name="ElectricityTransferred")

# Add constraints to ensure that the total electricity transferred from each power plant does not exceed its supply capacity
for p in range(P):
    model.addConstr(
        gp.quicksum(ElectricityTransferred[p, c] for c in range(C)) <= Supply[p],
        name=f"electricity_transfer_limit_{p}"
    )

# Ensure each city's electricity demand is satisfied
for c in range(C):
    model.addConstr(
        gp.quicksum(ElectricityTransferred[p, c] for p in range(P)) == Demand[c], 
        name=f"city_demand_satisfaction_{c}"
    )

# Add constraints to ensure the total electricity supplied to each city meets its demand
for c in range(C):
    model.addConstr(gp.quicksum(ElectricityTransferred[p, c] for p in range(P)) == Demand[c], name=f"demand_constraint_city_{c}")

# Add electricity transfer capacity constraints
for p in range(P):
    model.addConstr(gp.quicksum(ElectricityTransferred[p, c] for c in range(C)) <= Supply[p], name=f"electricity_transfer_capacity_{p}")

# Add non-negativity constraints for electricity transferred
for p in range(P):
    for c in range(C):
        model.addConstr(ElectricityTransferred[p, c] >= 0, name=f"non_negativity_p{p}_c{c}")

# Add electricity transfer constraints for each power plant
for p in range(P):
    model.addConstr(gp.quicksum(ElectricityTransferred[p, c] for c in range(C)) <= Supply[p], name=f"electricity_transfer_{p}")

# Add electricity demand constraints for each city
for c in range(C):
    model.addConstr(
        gp.quicksum(ElectricityTransferred[p, c] for p in range(P)) == Demand[c],
        name=f"electricity_demand_city_{c}"
    )

# Add non-negativity constraints for electricity transferred
for p in range(P):
    for c in range(C):
        model.addConstr(ElectricityTransferred[p, c] >= 0, name=f"non_negativity_{p}_{c}")

# Set objective
model.setObjective(gp.quicksum(TransmissionCosts[p, c] * ElectricityTransferred[p, c] for p in range(P) for c in range(C)), gp.GRB.MINIMIZE)

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
