import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_203/data.json", "r") as f:
    data = json.load(f)

BlackMilk = data["BlackMilk"] # scalar parameter
BlackHoney = data["BlackHoney"] # scalar parameter
MatchaMilk = data["MatchaMilk"] # scalar parameter
MatchaHoney = data["MatchaHoney"] # scalar parameter
ProfitBlack = data["ProfitBlack"] # scalar parameter
ProfitMatcha = data["ProfitMatcha"] # scalar parameter
TotalMilk = data["TotalMilk"] # scalar parameter
TotalHoney = data["TotalHoney"] # scalar parameter
BlackTeaBottles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BlackTeaBottles")
MatchaTeaBottles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MatchaTeaBottles")

# The variable BlackTeaBottles is inherently constrained to non-negative domain as it's defined as a continuous variable in Gurobi.

# The variable MatchaTeaBottles is already defined as non-negative (default for continuous variables in Gurobi)

# Add milk usage constraint for black and matcha milk teas
model.addConstr(
    BlackMilk * BlackTeaBottles + MatchaMilk * MatchaTeaBottles <= TotalMilk, 
    name="milk_usage_constraint"
)

# Add honey usage constraint for black and matcha milk tea production
model.addConstr(
    BlackHoney * BlackTeaBottles + MatchaHoney * MatchaTeaBottles <= TotalHoney,
    name="honey_usage_constraint"
)

# Add milk usage constraint
model.addConstr(BlackMilk * BlackTeaBottles + MatchaMilk * MatchaTeaBottles <= TotalMilk, name="milk_usage_constraint")

# Add constraint to ensure total honey required does not exceed total available honey
model.addConstr(BlackHoney * BlackTeaBottles + MatchaHoney * MatchaTeaBottles <= TotalHoney, name="honey_availability")

# Non-negativity is inherently ensured by the default lower bound of 0 in gurobipy variables.

# Non-negativity is inherent in the variable definition of MatchaTeaBottles,
# so no additional constraint code is required.

# Set objective
model.setObjective(ProfitBlack * BlackTeaBottles + ProfitMatcha * MatchaTeaBottles, gp.GRB.MAXIMIZE)

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
