import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_6/data.json", "r") as f:
    data = json.load(f)

TotalArea = data["TotalArea"] # scalar parameter
MaxRatioTomatoes = data["MaxRatioTomatoes"] # scalar parameter
MinTomatoes = data["MinTomatoes"] # scalar parameter
MinPotatoes = data["MinPotatoes"] # scalar parameter
ProfitTomatoes = data["ProfitTomatoes"] # scalar parameter
ProfitPotatoes = data["ProfitPotatoes"] # scalar parameter
AreaTomatoes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AreaTomatoes")
AreaPotatoes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AreaPotatoes")

# Add constraint for total area allocated to tomatoes and potatoes
model.addConstr(AreaTomatoes + AreaPotatoes <= TotalArea, name="total_area_constraint")

# Add minimum area constraint for tomatoes
model.addConstr(AreaTomatoes >= MinTomatoes, name="min_area_tomatoes")

# Add minimum area allocated to potatoes constraint
model.addConstr(AreaPotatoes >= MinPotatoes, name="min_potatoes_constraint")

# Add constraint to ensure the area of tomatoes does not exceed twice the area of potatoes
model.addConstr(AreaTomatoes <= MaxRatioTomatoes * AreaPotatoes, name="limit_tomato_area")

# No code needed: Non-negativity constraints are automatically handled in Gurobi by default for continuous variables.

# Add land allocation constraints
model.addConstr(AreaTomatoes + AreaPotatoes <= TotalArea, name="total_area_constraint")
model.addConstr(AreaTomatoes >= MinTomatoes, name="min_tomatoes_constraint")
model.addConstr(AreaPotatoes >= MinPotatoes, name="min_potatoes_constraint")
model.addConstr(AreaTomatoes <= MaxRatioTomatoes * AreaPotatoes, name="max_ratio_tomatoes_constraint")

# Add the constraint to ensure the area allocated to tomatoes meets the minimum required area
model.addConstr(AreaTomatoes >= MinTomatoes, name="min_tomato_area")

# Add the constraint to ensure the area allocated to potatoes meets the minimum required area
model.addConstr(AreaPotatoes >= MinPotatoes, name="min_area_potatoes")

# Add constraint to ensure that the ratio of AreaTomatoes to AreaPotatoes does not exceed MaxRatioTomatoes
model.addConstr(AreaTomatoes <= MaxRatioTomatoes * AreaPotatoes, name="tomatoes_to_potatoes_ratio")

# Ensure the total allocated area does not exceed the total available area
model.addConstr(AreaTomatoes + AreaPotatoes <= TotalArea, name="area_allocation_constraint")

# Add constraint ensuring the area ratio of tomatoes to potatoes does not exceed MaxRatioTomatoes
model.addConstr(AreaTomatoes <= MaxRatioTomatoes * AreaPotatoes, name="ratio_tomatoes_to_potatoes")

# Add constraint to ensure minimum area allocated for tomatoes
model.addConstr(AreaTomatoes >= MinTomatoes, name="min_area_tomatoes")

# Add constraint to ensure minimum area allocated for potatoes
model.addConstr(AreaPotatoes >= MinPotatoes, name="min_area_potatoes")

# The variable AreaTomatoes is already defined as non-negative due to its default properties in gurobipy (lower bound of 0).

# The variable AreaPotatoes is already defined as non-negative due to its default properties (continuous variables in Gurobi are non-negative unless stated otherwise); no additional constraint is needed.

# Set objective
model.setObjective(ProfitTomatoes * AreaTomatoes + ProfitPotatoes * AreaPotatoes, gp.GRB.MAXIMIZE)

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
