import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_248/data.json", "r") as f:
    data = json.load(f)

V = data["V"] # scalar parameter
F = data["F"] # scalar parameter
VSalad = data["VSalad"] # scalar parameter
FSalad = data["FSalad"] # scalar parameter
VFruitBowl = data["VFruitBowl"] # scalar parameter
FFruitBowl = data["FFruitBowl"] # scalar parameter
MaxFruitBowlProportion = data["MaxFruitBowlProportion"] # scalar parameter
KSalad = data["KSalad"] # scalar parameter
KFruitBowl = data["KFruitBowl"] # scalar parameter
NumberOfSalads = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfSalads")
NumberOfFruitBowls = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfFruitBowls")
S = model.addVar(vtype=gp.GRB.CONTINUOUS, name="S")
TotalMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMeals")

# Add vitamin intake constraint
model.addConstr(VSalad * NumberOfSalads + VFruitBowl * NumberOfFruitBowls >= V, name="vitamin_intake_constraint")

# Add minimum fibre intake constraint
model.addConstr(NumberOfSalads * FSalad + NumberOfFruitBowls * FFruitBowl >= F * S, name="minimum_fibre_intake")

# Add constraint to limit fruit bowls proportion
model.addConstr(
    NumberOfFruitBowls <= (MaxFruitBowlProportion / (1 - MaxFruitBowlProportion)) * NumberOfSalads,
    name="max_fruit_bowl_proportion"
)

# Add non-negativity constraint for the total number of salads
model.addConstr(NumberOfSalads >= 0, name="non_negative_salads")

# Add constraint to ensure the number of fruit bowls is non-negative
model.addConstr(NumberOfFruitBowls >= 0, name="non_negative_fruit_bowls")

# Add vitamin intake constraints
model.addConstr(VSalad * NumberOfSalads + VFruitBowl * NumberOfFruitBowls >= S * V, name="min_vitamin_intake")

# Add constraint to meet the minimum fibre intake requirement per staff
model.addConstr(FSalad * NumberOfSalads + FFruitBowl * NumberOfFruitBowls >= S * F, name="fibre_intake_requirement")

# Add constraint for total meals to be equal to the sum of salads and fruit bowls
model.addConstr(TotalMeals == NumberOfSalads + NumberOfFruitBowls, name="total_meals_constraint")

# Add constraint for the maximum proportion of fruit bowls
model.addConstr(NumberOfFruitBowls <= MaxFruitBowlProportion * TotalMeals, name="max_fruit_bowl_proportion")

# Set objective
model.setObjective(KSalad * NumberOfSalads + KFruitBowl * NumberOfFruitBowls, gp.GRB.MAXIMIZE)

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
