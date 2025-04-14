import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_155/data.json", "r") as f:
    data = json.load(f)

OtterTricks = data["OtterTricks"] # scalar parameter
OtterTreats = data["OtterTreats"] # scalar parameter
DolphinTricks = data["DolphinTricks"] # scalar parameter
DolphinTreats = data["DolphinTreats"] # scalar parameter
MinDolphins = data["MinDolphins"] # scalar parameter
MaxOtterProportion = data["MaxOtterProportion"] # scalar parameter
TotalTreats = data["TotalTreats"] # scalar parameter
NumberOfOtters = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfOtters")
NumberOfDolphins = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfDolphins")

# Add constraint for non-negative number of otters
model.addConstr(NumberOfOtters >= 0, name="non_negative_otters")

# Constraint to ensure the number of dolphins used is non-negative
model.addConstr(NumberOfDolphins >= 0, name="non_negative_dolphins")

# Add constraint for the minimum number of dolphins used in the shows
model.addConstr(NumberOfDolphins >= MinDolphins, name="min_dolphins_constraint")

# At most MaxOtterProportion of the performers can be otters constraint
model.addConstr(NumberOfOtters <= MaxOtterProportion * (NumberOfOtters + NumberOfDolphins), name="MaxOtterProportionConstraint")

# Total treats used by otters and dolphins cannot exceed the total available treats
model.addConstr(NumberOfOtters * OtterTricks * OtterTreats + NumberOfDolphins * DolphinTricks * DolphinTreats <= TotalTreats, "treats_limit")

# Treats constraint for otters and dolphins
model.addConstr(NumberOfOtters * OtterTreats + NumberOfDolphins * DolphinTreats <= TotalTreats, "treats_limit")

# Constraint for minimum number of dolphins used in the show
model.addConstr(NumberOfDolphins >= MinDolphins, name="min_dolphins_constraint")

# Proportion of performers that can be otters constraint
model.addConstr(NumberOfOtters <= MaxOtterProportion * (NumberOfOtters + NumberOfDolphins), name="OtterProportionConstraint")

# Set objective
model.setObjective(NumberOfOtters * OtterTricks + NumberOfDolphins * DolphinTricks, gp.GRB.MAXIMIZE)

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
