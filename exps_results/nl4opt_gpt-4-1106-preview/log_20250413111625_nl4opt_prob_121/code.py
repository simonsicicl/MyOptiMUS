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
RamenPacks = model.addVar(vtype=gp.GRB.INTEGER, name="RamenPacks")
FriesPacks = model.addVar(vtype=gp.GRB.INTEGER, name="FriesPacks")

# RamenPacks is already defined as a non-negative integer variable; hence no additional constraint is needed.

# Add non-negativity constraint for the number of fries packs
model.addConstr(FriesPacks >= 0, name="fries_packs_nonneg")

model.addConstr(RamenPacks <= MaxRamenFraction * (RamenPacks + FriesPacks), name="MaxRamenFractionConstraint")

# Add calorie consumption constraint
model.addConstr(CaloriesRamen * RamenPacks + CaloriesFries * FriesPacks >= MinCalories, name="min_calories")

# Add constraint for minimum protein intake
model.addConstr(ProteinRamen * RamenPacks + ProteinFries * FriesPacks >= MinProtein, name="min_protein_intake")

# Ensure the minimum total caloric intake is met
model.addConstr(CaloriesRamen * RamenPacks + CaloriesFries * FriesPacks >= MinCalories, name="min_caloric_intake")

# Ensure the minimum total protein intake is met
model.addConstr(ProteinRamen * RamenPacks + ProteinFries * FriesPacks >= MinProtein, name="min_protein_intake")

# Maximum fraction of meals that can be ramen constraint
model.addConstr(RamenPacks <= MaxRamenFraction * (RamenPacks + FriesPacks), name="max_ramen_fraction_constraint")

# Set objective
model.setObjective(SodiumRamen * RamenPacks + SodiumFries * FriesPacks, gp.GRB.MINIMIZE)

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
