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

# Add constraint for area allocation of tomatoes and potatoes not exceeding TotalArea
model.addConstr(AreaTomatoes + AreaPotatoes <= TotalArea, name="area_constraint")

# Constraint for minimum area allocated to tomatoes
model.addConstr(AreaTomatoes >= MinTomatoes, name="min_area_tomatoes_constraint")

# Ensure the area allocated for potatoes is at least the minimum required area
model.addConstr(AreaPotatoes >= MinPotatoes, name="min_potatoes_area")

# Add constraint for the area of tomatoes not to exceed twice the area of MaxRatioTomatoes in potatoes
model.addConstr(AreaTomatoes <= 2 * MaxRatioTomatoes * AreaPotatoes, name="tomato_potato_area_ratio")

# Since the variables AreaTomatoes and AreaPotatoes are defined with lower bounds of 0 by default in Gurobi,
# no additional constraints are needed to ensure their non-negativity.

# Total area allocated for tomatoes and potatoes must not exceed the total available area
model.addConstr(AreaTomatoes + AreaPotatoes <= TotalArea, "area_total_constraint")

# Area for tomatoes must be within the specified minimum requirements
model.addConstr(AreaTomatoes >= MinTomatoes, "area_tomatoes_min_constraint")

# Area for potatoes must be within the specified minimum requirements
model.addConstr(AreaPotatoes >= MinPotatoes, "area_potatoes_min_constraint")

# The maximum ratio of areas for tomatoes to potatoes must not be exceeded
model.addConstr(AreaTomatoes <= MaxRatioTomatoes * AreaPotatoes, "area_ratio_constraint")

# Add a constraint for the ratio of the area of tomatoes to the area of potatoes
# If the area of potatoes is zero, the constraint becomes non-binding
model.addConstr(AreaTomatoes - MaxRatioTomatoes * AreaPotatoes <= 0, name="tomatoes_to_potatoes_ratio")

# Constraint: The sum of areas for tomatoes and potatoes cannot exceed the total available area
model.addConstr(AreaTomatoes + AreaPotatoes <= TotalArea, "AreaConstraint")

# Add constraint to ensure the area for tomatoes is at least the minimum required
model.addConstr(AreaTomatoes >= MinTomatoes, name="min_area_tomatoes")

# Add constraint to ensure the area for potatoes is at least the minimum required
model.addConstr(AreaPotatoes >= MinPotatoes, name="min_area_potatoes")

# Add maximum ratio constraint for area of tomatoes to potatoes
model.addConstr(AreaTomatoes <= MaxRatioTomatoes * AreaPotatoes, name="TomatoesToPotatoesRatio")

# Set objective function
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
