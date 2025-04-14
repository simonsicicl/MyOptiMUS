import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_210/data.json", "r") as f:
    data = json.load(f)

RevenueLight = data["RevenueLight"] # scalar parameter
RevenueNonSticky = data["RevenueNonSticky"] # scalar parameter
RevenueHeavy = data["RevenueHeavy"] # scalar parameter
CompoundALight = data["CompoundALight"] # scalar parameter
CompoundBLight = data["CompoundBLight"] # scalar parameter
CompoundANonSticky = data["CompoundANonSticky"] # scalar parameter
CompoundBNonSticky = data["CompoundBNonSticky"] # scalar parameter
CompoundAHeavy = data["CompoundAHeavy"] # scalar parameter
CompoundBHeavy = data["CompoundBHeavy"] # scalar parameter
TotalCompoundA = data["TotalCompoundA"] # scalar parameter
TotalCompoundB = data["TotalCompoundB"] # scalar parameter
LightOilTanksProcessed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LightOilTanksProcessed")
NonStickyOilTanksProcessed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NonStickyOilTanksProcessed")
HeavyOilTanksProcessed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HeavyOilTanksProcessed")

# Add non-negativity constraint for LightOilTanksProcessed
model.addConstr(LightOilTanksProcessed >= 0, name="non_negative_LightOilTanksProcessed")

# The constraint is inherently satisfied as the non-sticky oil tanks processed variable,
# NonStickyOilTanksProcessed, has already been defined as a continuous variable in Gurobi,
# which ensures it can't implicitly be negative. No further constraint is needed.

# Ensure the number of heavy oil tanks processed is non-negative
model.addConstr(HeavyOilTanksProcessed >= 0, name="non_negative_heavy_oil_tanks")

# Add constraint for consumption of compound A by light oil processing
model.addConstr(LightOilTanksProcessed * CompoundALight <= TotalCompoundA, name="CompoundA_LightOil_Consumption")

# Add constraint for consumption of compound B for light oil
model.addConstr(LightOilTanksProcessed * CompoundBLight <= TotalCompoundB, name="CompoundB_LightOil_Consumption")

# Add constraint for the total consumption of compound A across all oils
model.addConstr(
    LightOilTanksProcessed * CompoundALight 
    + NonStickyOilTanksProcessed * CompoundANonSticky 
    + HeavyOilTanksProcessed * CompoundAHeavy 
    <= TotalCompoundA, 
    name="CompoundA_constraint"
)

# Add constraint on the total consumption of compound B
model.addConstr(
    CompoundBLight * LightOilTanksProcessed 
    + CompoundBNonSticky * NonStickyOilTanksProcessed 
    + CompoundBHeavy * HeavyOilTanksProcessed 
    <= TotalCompoundB, 
    name="CompoundB_constraint"
)

# Add constraint to ensure the total usage of compound A does not exceed the available amount
model.addConstr(
    (LightOilTanksProcessed * CompoundALight) +
    (NonStickyOilTanksProcessed * CompoundANonSticky) +
    (HeavyOilTanksProcessed * CompoundAHeavy)
    <= TotalCompoundA,
    name="TotalCompoundA_Constraint"
)

# Add constraint to ensure the total usage of compound B does not exceed the available amount
model.addConstr(
    (LightOilTanksProcessed * CompoundBLight) +
    (NonStickyOilTanksProcessed * CompoundBNonSticky) +
    (HeavyOilTanksProcessed * CompoundBHeavy)
    <= TotalCompoundB,
    name="TotalCompoundB_Constraint"
)

# Set objective
model.setObjective(
    (RevenueLight * LightOilTanksProcessed) + 
    (RevenueNonSticky * NonStickyOilTanksProcessed) + 
    (RevenueHeavy * HeavyOilTanksProcessed), 
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
