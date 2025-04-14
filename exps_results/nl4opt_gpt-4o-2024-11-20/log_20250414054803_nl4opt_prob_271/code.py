import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_271/data.json", "r") as f:
    data = json.load(f)

NorthernInjectionsRate = data["NorthernInjectionsRate"] # scalar parameter
NorthernCreamRate = data["NorthernCreamRate"] # scalar parameter
WesternInjectionsRate = data["WesternInjectionsRate"] # scalar parameter
WesternCreamRate = data["WesternCreamRate"] # scalar parameter
NorthernPlasticRate = data["NorthernPlasticRate"] # scalar parameter
WesternPlasticRate = data["WesternPlasticRate"] # scalar parameter
TotalPlastic = data["TotalPlastic"] # scalar parameter
MinInjections = data["MinInjections"] # scalar parameter
MinCream = data["MinCream"] # scalar parameter
NorthernHours = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NorthernHours")
WesternHours = model.addVar(vtype=gp.GRB.CONTINUOUS, name="WesternHours")
InjectionsProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InjectionsProduced")
CreamProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CreamProduced")

# Add constraint for total plastic usage across both factories not exceeding total available plastic
model.addConstr(
    NorthernPlasticRate * NorthernHours + WesternPlasticRate * WesternHours <= TotalPlastic,
    name="plastic_usage"
)

# Add constraint to ensure minimum production of anti-itch injections
model.addConstr(
    NorthernInjectionsRate * NorthernHours + WesternInjectionsRate * WesternHours >= MinInjections, 
    name="minimum_injections_production"
)

# Add constraint: The total cream produced must be at least MinCream.
model.addConstr(
    NorthernCreamRate * NorthernHours + WesternCreamRate * WesternHours >= MinCream,
    name="MinCream_Constraint"
)

# No code is needed: Gurobi variables by default have non-negativity constraints unless otherwise specified (e.g., if set to unrestricted).

# The variable WesternHours is already defined with the non-negativity implicitly ensured by Gurobi (default lower bound is non-negative).

# Add constraint to limit total plastic usage
model.addConstr(
    NorthernPlasticRate * NorthernHours + WesternPlasticRate * WesternHours <= TotalPlastic, 
    name="plastic_usage_limit"
)

# Add constraint to ensure total injections produced meets the requirement
model.addConstr(
    NorthernInjectionsRate * NorthernHours + WesternInjectionsRate * WesternHours == InjectionsProduced,
    name="total_injections_produced"
)

# Add constraint to ensure total injections produced meet or exceed the minimum required
model.addConstr(InjectionsProduced >= MinInjections, name="min_injections_constraint")

# Add total cream production constraint
model.addConstr(
    NorthernCreamRate * NorthernHours + WesternCreamRate * WesternHours == CreamProduced,
    name="total_cream_produced"
)

# Add constraint ensuring total cream produced is greater than or equal to the minimum required amount
model.addConstr(CreamProduced >= MinCream, name="min_cream_constraint")

# Set objective
model.setObjective(NorthernHours + WesternHours, gp.GRB.MINIMIZE)

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
