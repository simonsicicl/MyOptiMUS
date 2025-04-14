import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/3/data.json", "r") as f:
    data = json.load(f)

T = data["T"] # scalar parameter
Demand = np.array(data["Demand"]) # ['T']
OilCap = np.array(data["OilCap"]) # ['T']
CoalCost = data["CoalCost"] # scalar parameter
NukeCost = data["NukeCost"] # scalar parameter
MaxNuke = data["MaxNuke"] # scalar parameter
CoalLife = data["CoalLife"] # scalar parameter
NukeLife = data["NukeLife"] # scalar parameter
CoalProd = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="CoalProd")
OilProd = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="OilProd")
NukeProd = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="NukeProd")

# Add constraints to meet energy demand in each period
for t in range(T):
    model.addConstr(CoalProd[t] + OilProd[t] + NukeProd[t] >= Demand[t], name=f"energy_demand_{t}")

# Add energy production and capacity constraints for oil
for t in range(T):
    model.addConstr(OilProd[t] <= OilCap[t], name=f"oil_capacity_t{t}")

# Add nuclear energy production capacity constraints
for t in range(T):
    model.addConstr(NukeProd[t] <= MaxNuke, name=f"NukeProd_capacity_{t}")

# Add constraints to ensure oil production does not exceed its capacity in each period t
for t in range(T):
    model.addConstr(OilProd[t] <= OilCap[t], name=f"oil_production_capacity_{t}")

# Add nuclear production capacity constraints
for t in range(T):
    model.addConstr(NukeProd[t] <= MaxNuke, name=f"NukeProd_capacity_{t}")

# Add non-negativity constraint for coal production
for t in range(T):
    model.addConstr(CoalProd[t] >= 0, name=f"non_negative_CoalProd_{t}")

# Add non-negativity constraint for oil production
for t in range(T):
    model.addConstr(OilProd[t] >= 0, name=f"non_negative_OilProd_{t}")

# Ensure nuclear production is non-negative
for t in range(T):
    model.addConstr(NukeProd[t] >= 0, name=f"NukeProd_non_negative_{t}")

# Add constraints to ensure energy production meets or exceeds demand in each period
for t in range(T):
    model.addConstr(CoalProd[t] + OilProd[t] + NukeProd[t] >= Demand[t], name=f"energy_meets_demand_t{t}")

# Add constraints to restrict oil production to its maximum capacity
for t in range(T):
    model.addConstr(OilProd[t] <= OilCap[t], name=f"oil_production_limit_{t}")

# Add nuclear production capacity constraints
for t in range(T):
    model.addConstr(NukeProd[t] <= MaxNuke, name=f"nuclear_capacity_{t}")

# Set objective
model.setObjective(gp.quicksum(CoalCost * CoalProd[t] + NukeCost * NukeProd[t] for t in range(T)), gp.GRB.MINIMIZE)

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
