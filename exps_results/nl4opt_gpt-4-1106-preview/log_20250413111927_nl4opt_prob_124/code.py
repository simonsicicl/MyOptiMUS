import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_124/data.json", "r") as f:
    data = json.load(f)

MgGummy = data["MgGummy"] # scalar parameter
ZnGummy = data["ZnGummy"] # scalar parameter
MgPill = data["MgPill"] # scalar parameter
ZnPill = data["ZnPill"] # scalar parameter
MinPills = data["MinPills"] # scalar parameter
GummyPillRatio = data["GummyPillRatio"] # scalar parameter
MaxMg = data["MaxMg"] # scalar parameter
NumGummies = model.addVar(vtype=gp.GRB.INTEGER, name="NumGummies")
NumPills = model.addVar(vtype=gp.GRB.INTEGER, name="NumPills")

# Add non-negativity constraint for the number of gummies
model.addConstr(NumGummies >= 0, name="non_negativity_NumGummies")

# The number of pills the boy consumes must be non-negative
model.addConstr(NumPills >= 0, name="num_pills_non_negative")

# Add constraint for minimum number of pills consumption
model.addConstr(NumPills >= MinPills, name="min_pills_consumption")

# Add constraint to ensure the boy eats at least GummyPillRatio times the number of gummies as pills
model.addConstr(NumGummies >= GummyPillRatio * NumPills, name="gummy_pill_ratio")

# Total magnesium from gummies and pills constraint
model.addConstr(NumGummies * MgGummy + NumPills * MgPill <= MaxMg, name="max_magnesium")

# Add constraint for maximum magnesium intake from gummies and pills
model.addConstr(NumGummies * MgGummy + NumPills * MgPill <= MaxMg, name="max_magnesium")

# Add constraint for minimum number of pills
model.addConstr(NumPills >= MinPills, name="min_pills_constraint")

# Constraint: The number of gummies must be at least three times the number of pills
model.addConstr(NumGummies >= GummyPillRatio * NumPills, name="gummies_to_pills_ratio")

# Define the objective function
model.setObjective(NumGummies * ZnGummy + NumPills * ZnPill, gp.GRB.MAXIMIZE)

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
