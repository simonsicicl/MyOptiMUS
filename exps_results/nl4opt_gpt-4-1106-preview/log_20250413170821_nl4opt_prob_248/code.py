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
NumSalads = model.addVar(vtype=gp.GRB.INTEGER, name="NumSalads")
NumFruitBowls = model.addVar(vtype=gp.GRB.INTEGER, name="NumFruitBowls")

# Each staff must receive at least V units of vitamins from salads and fruit bowls
model.addConstr(VSalad * NumSalads + VFruitBowl * NumFruitBowls >= V, name="vitamin_intake")

# Ensure each staff member receives at least F units of fibre
model.addConstr(NumSalads * FSalad + NumFruitBowls * FFruitBowl >= F, name="min_fibre_intake")

# Each staff is limited to a maximum proportion of MaxFruitBowlProportion of their total meals as fruit bowls
model.addConstr(NumFruitBowls <= MaxFruitBowlProportion * (NumSalads + NumFruitBowls), "max_fruit_bowl_proportion")

# Since NumSalads is a scalar and already defined as an integer variable, we just need to add the non-negativity constraint
model.addConstr(NumSalads >= 0, name="salads_non_negative")

# Since NumFruitBowls is already an integer variable, we only need to add the constraint that it is non-negative
model.addConstr(NumFruitBowls >= 0, "NumFruitBowls_nonnegativity")

# Set objective function
TotalPotassiumIntake = NumSalads * KSalad + NumFruitBowls * KFruitBowl
model.setObjective(TotalPotassiumIntake, gp.GRB.MAXIMIZE)

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
