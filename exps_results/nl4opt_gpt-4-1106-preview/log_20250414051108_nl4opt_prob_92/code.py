import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_92/data.json", "r") as f:
    data = json.load(f)

ToysMedium = data["ToysMedium"] # scalar parameter
OperatorsMedium = data["OperatorsMedium"] # scalar parameter
ToysSmall = data["ToysSmall"] # scalar parameter
OperatorsSmall = data["OperatorsSmall"] # scalar parameter
ToysMin = data["ToysMin"] # scalar parameter
OperatorsTotal = data["OperatorsTotal"] # scalar parameter
MediumFactories = model.addVar(vtype=gp.GRB.INTEGER, name="MediumFactories")
SmallFactories = model.addVar(vtype=gp.GRB.INTEGER, name="SmallFactories")

# Add constraint to ensure the number of medium-sized factories is non-negative
model.addConstr(MediumFactories >= 0, name="MediumFactories_non_negative")

# Small factories number should be non-negative (Redundant: Gurobi handles this through variable declaration)
# No additional constraint code needed because non-negativity is ensured by the variable type (INTEGER) in Gurobi.

# Add constraint for meeting minimum daily production requirement
model.addConstr(MediumFactories * ToysMedium + SmallFactories * ToysSmall >= ToysMin, name="min_daily_production")

# Ensure total number of operators for medium and small factories does not exceed operators available
model.addConstr(OperatorsMedium * MediumFactories + OperatorsSmall * SmallFactories <= OperatorsTotal, name="operator_availability")

# Add production constraint to meet the minimum daily toy production requirement
model.addConstr(ToysMedium * MediumFactories + ToysSmall * SmallFactories >= ToysMin, name="production_constraint")

model.addConstr(OperatorsMedium * MediumFactories + OperatorsSmall * SmallFactories <= OperatorsTotal, name="operator_constraint")

# Set objective
model.setObjective(MediumFactories + SmallFactories, gp.GRB.MINIMIZE)

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
