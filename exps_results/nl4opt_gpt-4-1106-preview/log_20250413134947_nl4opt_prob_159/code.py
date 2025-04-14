import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_159/data.json", "r") as f:
    data = json.load(f)

TruckCapacity = data["TruckCapacity"] # scalar parameter
TruckCost = data["TruckCost"] # scalar parameter
VanCapacity = data["VanCapacity"] # scalar parameter
VanCost = data["VanCost"] # scalar parameter
MinPatties = data["MinPatties"] # scalar parameter
Budget = data["Budget"] # scalar parameter
NumTrucks = model.addVar(vtype=gp.GRB.INTEGER, name="NumTrucks")
NumVans = model.addVar(vtype=gp.GRB.INTEGER, name="NumVans")

# Ensure the number of trucks and vans used is non-negative
model.addConstr(NumTrucks >= 0, name="num_trucks_non_negative")
model.addConstr(NumVans >= 0, name="num_vans_non_negative")

# The number of vans used is non-negative by the variable definition (integer variable by default is >= 0)
# No additional constraints are needed

model.addConstr(NumTrucks <= NumVans, name="Trucks_leq_Vans")

# Ensure at least MinPatties patties are shipped
model.addConstr(NumTrucks * TruckCapacity + NumVans * VanCapacity >= MinPatties, name="min_patties_shipped")

# Constraint: Total cost of trucks and vans must not exceed budget
model.addConstr(TruckCost * NumTrucks + VanCost * NumVans <= Budget, name="budget_constraint")

# Ensure the minimum number of patties are shipped
model.addConstr(NumTrucks * TruckCapacity + NumVans * VanCapacity >= MinPatties, name="min_patties_shipped")

# Ensure that the budget is not exceeded
model.addConstr(NumTrucks * TruckCost + NumVans * VanCost <= Budget, "budget_constraint")

# Set objective
model.setObjective(NumTrucks + NumVans, gp.GRB.MINIMIZE)

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
