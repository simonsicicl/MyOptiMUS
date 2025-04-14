import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_252/data.json", "r") as f:
    data = json.load(f)

LargeUnitCapacity = data["LargeUnitCapacity"] # scalar parameter
LargeUnitSpots = data["LargeUnitSpots"] # scalar parameter
SmallUnitCapacity = data["SmallUnitCapacity"] # scalar parameter
SmallUnitSpots = data["SmallUnitSpots"] # scalar parameter
MinSmallUnits = data["MinSmallUnits"] # scalar parameter
MinLargeUnitProportion = data["MinLargeUnitProportion"] # scalar parameter
TotalPeople = data["TotalPeople"] # scalar parameter
LargeUnits = model.addVar(vtype=gp.GRB.INTEGER, name="LargeUnits")
SmallUnits = model.addVar(vtype=gp.GRB.INTEGER, name="SmallUnits")

model.addConstr(LargeUnits >= 0, name="non_negativity_large_units")

model.addConstr(SmallUnits >= 0, name="non_negativity_small_units")

# At least a minimum number of small units are required
model.addConstr(SmallUnits >= MinSmallUnits, name="min_small_units_constraint")

# Add constraint for minimum proportion of large units
model.addConstr(LargeUnits >= MinLargeUnitProportion * (LargeUnits + SmallUnits), name="min_large_unit_proportion")

# Add a constraint that the sum of people carried by large and small units must be equal to or exceed TotalPeople
model.addConstr(LargeUnits * LargeUnitCapacity + SmallUnits * SmallUnitCapacity >= TotalPeople, "people_capacity")

# Add total capacity constraint
model.addConstr(LargeUnits * LargeUnitCapacity + SmallUnits * SmallUnitCapacity >= TotalPeople, name="total_capacity")

model.addConstr(SmallUnits >= MinSmallUnits, name="min_small_units")

# Add constraint for minimum required proportion of large units
model.addConstr(LargeUnits >= MinLargeUnitProportion * (LargeUnits + SmallUnits), name="min_large_units_proportion")

# Define the objective function
model.setObjective(LargeUnitSpots * LargeUnits + SmallUnitSpots * SmallUnits, gp.GRB.MINIMIZE)

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
