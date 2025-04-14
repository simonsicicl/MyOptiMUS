import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_131/data.json", "r") as f:
    data = json.load(f)

BananaCalories = data["BananaCalories"] # scalar parameter
BananaPotassium = data["BananaPotassium"] # scalar parameter
BananaSugar = data["BananaSugar"] # scalar parameter
MangoCalories = data["MangoCalories"] # scalar parameter
MangoPotassium = data["MangoPotassium"] # scalar parameter
MangoSugar = data["MangoSugar"] # scalar parameter
MinCalories = data["MinCalories"] # scalar parameter
MinPotassium = data["MinPotassium"] # scalar parameter
MaxMangoPercentage = data["MaxMangoPercentage"] # scalar parameter
NumberOfBananas = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBananas")
NumberOfMangoes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfMangoes")
TotalFruits = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalFruits")

# Add non-negativity constraint for NumberOfBananas
model.addConstr(NumberOfBananas >= 0, name="nonnegativity_constraint_NumberOfBananas")

# Constraint to ensure the number of mangoes in the gorilla's diet is non-negative
model.addConstr(NumberOfMangoes >= 0, name="non_negative_mangoes")

# Add calorie intake constraint for the gorilla
model.addConstr(NumberOfBananas * BananaCalories + NumberOfMangoes * MangoCalories >= MinCalories, name="calorie_intake_constraint")

# Add potassium intake constraint
model.addConstr(NumberOfBananas * BananaPotassium + NumberOfMangoes * MangoPotassium >= MinPotassium, name="potassium_intake")

# Add constraint to enforce that at most MaxMangoPercentage of the fruit can be mangoes
model.addConstr((1 - MaxMangoPercentage) * NumberOfMangoes <= MaxMangoPercentage * NumberOfBananas, name="mango_percentage_limit")

# Add calorie requirement constraint
model.addConstr(
    BananaCalories * NumberOfBananas + MangoCalories * NumberOfMangoes >= MinCalories,
    name="min_calorie_requirement"
)

# Add potassium requirement constraint
model.addConstr(
    BananaPotassium * NumberOfBananas + MangoPotassium * NumberOfMangoes >= MinPotassium,
    name="min_potassium_requirement"
)

# Add constraint to ensure mangoes do not exceed the maximum percentage of the gorilla's diet
model.addConstr(NumberOfMangoes <= MaxMangoPercentage * TotalFruits, name="max_mango_percentage")

# Add constraint for total fruits equality
model.addConstr(TotalFruits == NumberOfBananas + NumberOfMangoes, name="total_fruits_constraint")

# Set objective
model.setObjective(BananaSugar * NumberOfBananas + MangoSugar * NumberOfMangoes, gp.GRB.MINIMIZE)

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
