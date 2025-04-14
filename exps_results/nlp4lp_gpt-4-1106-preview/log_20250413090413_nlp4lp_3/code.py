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
EnergyProducedOil = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="EnergyProducedOil")
EnergyProducedCoal = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="EnergyProducedCoal")
EnergyProducedNuke = model.addVars(T, vtype=gp.GRB.CONTINUOUS, name="EnergyProducedNuke")
OilCostPerUnit = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OilCostPerUnit")

# Meet the energy demand in each period T
for t in range(T):
    model.addConstr(gp.quicksum([EnergyProducedOil[t], EnergyProducedCoal[t], EnergyProducedNuke[t]]) >= Demand[t], name=f"energy_demand_{t}")

# Add constraints to not exceed the maximum oil capacity in each period T
for t in range(T):
    model.addConstr(EnergyProducedOil[t] <= OilCap[t], name=f"max_oil_capacity_{t}")

# Add the constraint for maximum nuclear power production in any period
for t in range(T):
    model.addConstr(EnergyProducedNuke[t] <= MaxNuke, name=f"max_nuclear_capacity_period_{t}")

# Set the objective function
model.setObjective(gp.quicksum(
    EnergyProducedOil[t] * OilCostPerUnit + 
    EnergyProducedCoal[t] * CoalCost +
    EnergyProducedNuke[t] * NukeCost
    for t in range(T)), gp.GRB.MINIMIZE)

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
