import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_107/data.json", "r") as f:
    data = json.load(f)

ProteinFish = data["ProteinFish"] # scalar parameter
IronFish = data["IronFish"] # scalar parameter
ProteinChicken = data["ProteinChicken"] # scalar parameter
IronChicken = data["IronChicken"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
MinIron = data["MinIron"] # scalar parameter
MinChickenFishRatio = data["MinChickenFishRatio"] # scalar parameter
FatFish = data["FatFish"] # scalar parameter
FatChicken = data["FatChicken"] # scalar parameter
NumberOfFishMeals = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfFishMeals")
NumberOfChickenMeals = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfChickenMeals")

# Patient protein intake constraint
model.addConstr(ProteinFish * NumberOfFishMeals + ProteinChicken * NumberOfChickenMeals >= MinProtein, name="min_protein_intake")

# Ensure patient's diet contains at least the minimum required units of iron
model.addConstr(IronFish * NumberOfFishMeals + IronChicken * NumberOfChickenMeals >= MinIron, name="min_iron_requirement")

# Since NumberOfFishMeals has already been defined as an integer variable, 
# we just need to add a constraint to ensure it is non-negative
model.addConstr(NumberOfFishMeals >= 0, name="non_negative_fish_meals")

model.addConstr(NumberOfChickenMeals >= 0, name="nonnegativity_chicken_meals")

# Ensure the patient consumes at least the minimum required units of protein
model.addConstr(ProteinFish * NumberOfFishMeals + ProteinChicken * NumberOfChickenMeals >= MinProtein, name="min_protein_requirement")

# Ensure the patient consumes at least the minimum required units of iron
model.addConstr(IronFish * NumberOfFishMeals + IronChicken * NumberOfChickenMeals >= MinIron, "min_iron_intake")

# Ensure the number of chicken meals is at least twice the number of fish meals
model.addConstr(MinChickenFishRatio * NumberOfFishMeals <= NumberOfChickenMeals, "Min_Chicken_Fish_Ratio")

# Set objective
model.setObjective(FatFish * NumberOfFishMeals + FatChicken * NumberOfChickenMeals, gp.GRB.MINIMIZE)

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
