import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_216/data.json", "r") as f:
    data = json.load(f)

TotalBatter = data["TotalBatter"] # scalar parameter
TotalMilk = data["TotalMilk"] # scalar parameter
BatterCrepe = data["BatterCrepe"] # scalar parameter
MilkCrepe = data["MilkCrepe"] # scalar parameter
BatterSponge = data["BatterSponge"] # scalar parameter
MilkSponge = data["MilkSponge"] # scalar parameter
BatterBirthday = data["BatterBirthday"] # scalar parameter
MilkBirthday = data["MilkBirthday"] # scalar parameter
ProfitCrepe = data["ProfitCrepe"] # scalar parameter
ProfitSponge = data["ProfitSponge"] # scalar parameter
ProfitBirthday = data["ProfitBirthday"] # scalar parameter
NumberOfCrepeCakes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCrepeCakes")
NumberOfSpongeCakes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSpongeCakes")
NumberOfBirthdayCakes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBirthdayCakes")

# Constraint to ensure the number of crepe cakes produced is non-negative
model.addConstr(NumberOfCrepeCakes >= 0, name="non_negative_crepe_cakes")

# Since the variable NumberOfSpongeCakes is already declared as an integer variable, we just need to add the constraint
model.addConstr(NumberOfSpongeCakes >= 0, "sponge_cakes_non_negative")

# Since NumberOfBirthdayCakes is already defined as an integer variable, we just need to add a constraint to ensure it is non-negative
model.addConstr(NumberOfBirthdayCakes >= 0, name="non_negative_cakes")

# Constraint: Total grams of batter used for all cakes cannot exceed the total available batter
model.addConstr(NumberOfCrepeCakes * BatterCrepe + NumberOfSpongeCakes * BatterSponge + NumberOfBirthdayCakes * BatterBirthday <= TotalBatter, name="TotalBatterConstraint")

# Total milk usage constraint
model.addConstr(NumberOfCrepeCakes * MilkCrepe + NumberOfSpongeCakes * MilkSponge +
                NumberOfBirthdayCakes * MilkBirthday <= TotalMilk, name="total_milk_usage")

# Define the objective function
model.setObjective(ProfitCrepe * NumberOfCrepeCakes + ProfitSponge * NumberOfSpongeCakes + ProfitBirthday * NumberOfBirthdayCakes, gp.GRB.MAXIMIZE)

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
