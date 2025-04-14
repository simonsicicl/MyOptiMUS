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
NumberOfBananas = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBananas")
NumberOfMangoes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMangoes")

# Add non-negativity constraint for the number of bananas
model.addConstr(NumberOfBananas >= 0, name="nonnegativity_bananas")

# Add constraint for non-negative number of mangoes
model.addConstr(NumberOfMangoes >= 0, name="non_negative_mangoes")

# Constraint: Total calories consumed by the gorilla must be at least MinCalories
model.addConstr(NumberOfBananas * BananaCalories + NumberOfMangoes * MangoCalories >= MinCalories, name="min_calories")

# Constraint for minimum potassium consumption by the gorilla
model.addConstr(BananaPotassium * NumberOfBananas + MangoPotassium * NumberOfMangoes >= MinPotassium, name="min_potassium")

# At most MaxMangoPercentage of the fruits can be mangoes constraint
model.addConstr(NumberOfMangoes <= MaxMangoPercentage * (NumberOfBananas + NumberOfMangoes), name="max_mango_percentage")

# Constraint: The total calories from bananas and mangoes must meet the gorilla's minimum caloric requirements
model.addConstr(BananaCalories * NumberOfBananas + MangoCalories * NumberOfMangoes >= MinCalories, "min_calories_requirement")

# Ensure the total grams of potassium from bananas and mangoes meet the gorilla's minimum requirement
model.addConstr(BananaPotassium * NumberOfBananas + MangoPotassium * NumberOfMangoes >= MinPotassium, "potassium_requirement")

# Mangoes cannot exceed a certain percentage of the total number of fruits in the gorilla's diet
MaxMangoPercentage = data["MaxMangoPercentage"]  # scalar parameter
model.addConstr(NumberOfMangoes <= MaxMangoPercentage * (NumberOfBananas + NumberOfMangoes), name="mango_percentage_constraint")

# Define the objective function
TotalSugarIntake = BananaSugar * NumberOfBananas + MangoSugar * NumberOfMangoes

# Set the objective: Minimize the total sugar intake
model.setObjective(TotalSugarIntake, gp.GRB.MINIMIZE)

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
