import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_121/data.json", "r") as f:
    data = json.load(f)

CaloriesRamen = data["CaloriesRamen"] # scalar parameter
ProteinRamen = data["ProteinRamen"] # scalar parameter
SodiumRamen = data["SodiumRamen"] # scalar parameter
CaloriesFries = data["CaloriesFries"] # scalar parameter
ProteinFries = data["ProteinFries"] # scalar parameter
SodiumFries = data["SodiumFries"] # scalar parameter
MaxRamenFraction = data["MaxRamenFraction"] # scalar parameter
MinCalories = data["MinCalories"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
NumberOfRamenPacks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfRamenPacks")
NumberOfFriesPacks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfFriesPacks")
TotalMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMeals")

# Add non-negativity constraint for NumberOfRamenPacks
model.addConstr(NumberOfRamenPacks >= 0, name="non_negativity_NumberOfRamenPacks")

# The variable 'NumberOfFriesPacks' is already defined as a continuous variable, so no constraint is needed to ensure non-negativity. Gurobi ensures non-negativity by default for continuous variables.

# Add constraint to limit the proportion of ramen packs consumed
model.addConstr(NumberOfRamenPacks * (1 - MaxRamenFraction) <= MaxRamenFraction * NumberOfFriesPacks, name="ramen_fraction_limit")

# Ensure the salesman consumes at least the minimum required calories from ramen and fries.
model.addConstr(
    (NumberOfRamenPacks * CaloriesRamen) + (NumberOfFriesPacks * CaloriesFries) >= MinCalories, 
    name="calories_constraint"
)

# Add minimum protein intake constraint
model.addConstr(
    ProteinRamen * NumberOfRamenPacks + ProteinFries * NumberOfFriesPacks >= MinProtein,
    name="min_protein_intake"
)

# Add caloric intake constraint
model.addConstr(
    CaloriesRamen * NumberOfRamenPacks + CaloriesFries * NumberOfFriesPacks >= MinCalories,
    name="caloric_intake"
)

# Add protein intake constraint
model.addConstr(
    ProteinRamen * NumberOfRamenPacks + ProteinFries * NumberOfFriesPacks >= MinProtein, 
    name="protein_intake_constraint"
)

# Add constraint to ensure the fraction of meals from ramen does not exceed MaxRamenFraction
model.addConstr(NumberOfRamenPacks <= MaxRamenFraction * TotalMeals, name="ramen_fraction_limit")

# Add constraint to define TotalMeals as the sum of NumberOfRamenPacks and NumberOfFriesPacks
model.addConstr(TotalMeals == NumberOfRamenPacks + NumberOfFriesPacks, name="total_meals_definition")

# Set objective
model.setObjective(SodiumRamen * NumberOfRamenPacks + SodiumFries * NumberOfFriesPacks, gp.GRB.MINIMIZE)

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
