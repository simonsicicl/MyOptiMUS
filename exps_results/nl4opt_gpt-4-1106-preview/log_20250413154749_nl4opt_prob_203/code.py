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
NumberOfBlackMilkTeaBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBlackMilkTeaBottles")
NumberOfMatchaMilkTeaBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMatchaMilkTeaBottles")

# Since NumberOfBlackMilkTeaBottles is already defined as an integer variable, we just need to add the non-negativity constraint
model.addConstr(NumberOfBlackMilkTeaBottles >= 0, "non_negativity_black_milk_tea_bottles")

# The NumberOfMatchaMilkTeaBottles variable is already non-negative by the nature of its definition as an INTEGER in the code provided.
# Therefore, no additional constraint is required to ensure its non-negativity.

# Total milk used for black and matcha milk teas does not exceed TotalMilk grams
model.addConstr((BlackMilk * NumberOfBlackMilkTeaBottles) + 
                (MatchaMilk * NumberOfMatchaMilkTeaBottles) <= TotalMilk,
                name="milk_usage_constraint")

# Total honey used for black and matcha milk teas does not exceed TotalHoney grams
model.addConstr(BlackHoney * NumberOfBlackMilkTeaBottles + MatchaHoney * NumberOfMatchaMilkTeaBottles <= TotalHoney, name="honey_usage_constraint")

# Milk usage constraint for black and matcha milk tea bottles
model.addConstr((BlackMilk * NumberOfBlackMilkTeaBottles + MatchaMilk * NumberOfMatchaMilkTeaBottles) <= TotalMilk, name="milk_usage")

# Constraint: Total honey used for black and matcha milk tea should not exceed the total amount of honey available
model.addConstr((BlackHoney * NumberOfBlackMilkTeaBottles + MatchaHoney * NumberOfMatchaMilkTeaBottles) <= TotalHoney, "honey_usage_constraint")

# Define variables
NumberOfBlackMilkTeaBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBlackMilkTeaBottles")
NumberOfMatchaMilkTeaBottles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMatchaMilkTeaBottles")

# Define parameters
ProfitBlack = data["ProfitBlack"]  # 7.5
ProfitMatcha = data["ProfitMatcha"]  # 5.0

# Set objective
model.setObjective(ProfitBlack * NumberOfBlackMilkTeaBottles + ProfitMatcha * NumberOfMatchaMilkTeaBottles, gp.GRB.MAXIMIZE)

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
