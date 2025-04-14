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
LargeUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LargeUnits")
SmallUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SmallUnits")
TotalUnits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalUnits")

# Non-negativity constraint for LargeUnits
model.addConstr(LargeUnits >= 0, name="non_negativity_LargeUnits")

# Non-negativity constraint for SmallUnits
model.addConstr(SmallUnits >= 0, name="non_negativity_SmallUnits")

# Add constraint to enforce minimum number of small mobile units
model.addConstr(SmallUnits >= MinSmallUnits, name="min_small_units")

# Add constraint: large mobile units must constitute at least MinLargeUnitProportion of all vehicles
model.addConstr((1 - MinLargeUnitProportion) * LargeUnits >= MinLargeUnitProportion * SmallUnits, name="MinLargeUnitProportion_constraint")

# Add constraint to ensure the total people carried by large and small units meets or exceeds TotalPeople
model.addConstr(
    LargeUnits * LargeUnitCapacity + SmallUnits * SmallUnitCapacity >= TotalPeople,
    name="people_transport_constraint"
)

# Ensure total capacity of mobile units accommodates all people
model.addConstr(
    LargeUnits * LargeUnitCapacity + SmallUnits * SmallUnitCapacity >= TotalPeople,
    name="capacity_constraint"
)

# Add constraint for minimum number of small mobile production units
model.addConstr(SmallUnits >= MinSmallUnits, name="min_small_units")

# Add constraint for the minimum proportion of large mobile production units
model.addConstr(
    (1 - MinLargeUnitProportion) * LargeUnits - MinLargeUnitProportion * SmallUnits >= 0,
    name="min_large_unit_proportion"
)

# Add constraint for TotalUnits definition
model.addConstr(TotalUnits == LargeUnits + SmallUnits, name="total_units_definition")

# Set objective
model.setObjective(LargeUnits * LargeUnitSpots + SmallUnits * SmallUnitSpots, gp.GRB.MINIMIZE)

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
