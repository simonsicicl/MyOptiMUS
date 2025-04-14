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
FishMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FishMeals")
ChickenMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ChickenMeals")

# Add constraint to ensure at least the minimum required protein is consumed
model.addConstr(FishMeals * ProteinFish + ChickenMeals * ProteinChicken >= MinProtein, name="min_protein_requirement")

# Add the constraint to ensure the patient consumes at least the minimum required units of iron
model.addConstr(
    FishMeals * IronFish + ChickenMeals * IronChicken >= MinIron,
    name="min_iron_requirement"
)

# The non-negativity constraint for FishMeals is implicitly satisfied by its definition as a continuous variable which is non-negative by default.

# No code needed as the non-negativity constraint is inherently satisfied by the variable type (continuous by default is >= 0 in Gurobi).

# Add protein intake constraint
model.addConstr(FishMeals * ProteinFish + ChickenMeals * ProteinChicken >= MinProtein, name="protein_requirement")

# Add constraint to ensure the total iron intake meets the minimum requirement
model.addConstr(FishMeals * IronFish + ChickenMeals * IronChicken >= MinIron, name="min_iron_intake")

# Add constraint to ensure the minimum ratio of chicken meals to fish meals is maintained
model.addConstr(ChickenMeals >= MinChickenFishRatio * FishMeals, name="min_chicken_fish_ratio_constraint")

# Set objective
model.setObjective(FatFish * FishMeals + FatChicken * ChickenMeals, gp.GRB.MINIMIZE)

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
