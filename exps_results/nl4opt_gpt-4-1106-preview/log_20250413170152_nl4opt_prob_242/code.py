import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_242/data.json", "r") as f:
    data = json.load(f)

CaloriesSalmon = data["CaloriesSalmon"] # scalar parameter
ProteinSalmon = data["ProteinSalmon"] # scalar parameter
SodiumSalmon = data["SodiumSalmon"] # scalar parameter
CaloriesEggs = data["CaloriesEggs"] # scalar parameter
ProteinEggs = data["ProteinEggs"] # scalar parameter
SodiumEggs = data["SodiumEggs"] # scalar parameter
MaxEggProportion = data["MaxEggProportion"] # scalar parameter
MinTotalCalories = data["MinTotalCalories"] # scalar parameter
MinTotalProtein = data["MinTotalProtein"] # scalar parameter
SalmonBowls = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SalmonBowls")
EggMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="EggMeals")

# Add constraint for non-negative number of salmon meals
model.addConstr(SalmonBowls >= 0, name="non_negative_salmon")

model.addConstr(EggMeals >= 0, name="EggMeals_non_negative")

# At most MaxEggProportion of the meals can be eggs
model.addConstr(EggMeals <= MaxEggProportion * (EggMeals + SalmonBowls), name="max_egg_proportion_constraint")

# Constraint for minimum total caloric intake
model.addConstr(CaloriesSalmon * SalmonBowls + CaloriesEggs * EggMeals >= MinTotalCalories, "min_calories_intake")

# Total protein intake constraint
model.addConstr(ProteinSalmon * SalmonBowls + ProteinEggs * EggMeals >= MinTotalProtein, "min_protein_requirement")

# Ensure the calorie intake from bowls of salmon and eggs meets the minimum required
model.addConstr(CaloriesSalmon * SalmonBowls + CaloriesEggs * EggMeals >= MinTotalCalories, "calorie_intake_constraint")

# Ensure the protein intake from bowls of salmon and eggs meets the minimum required
model.addConstr(ProteinSalmon * SalmonBowls + ProteinEggs * EggMeals >= MinTotalProtein, name="min_protein_intake")

model.addConstr(SalmonBowls + EggMeals <= 1/MaxEggProportion * EggMeals, name="limit_egg_proportion")

# Define the objective function
model.setObjective(SodiumSalmon * SalmonBowls + SodiumEggs * EggMeals, gp.GRB.MINIMIZE)

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
