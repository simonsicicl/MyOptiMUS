import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/diet/data.json", "r") as f:
    data = json.load(f)

NutrientCount = data["NutrientCount"] # scalar parameter
FoodCount = data["FoodCount"] # scalar parameter
Cost = np.array(data["Cost"]) # ['FoodCount']
FoodMin = np.array(data["FoodMin"]) # ['FoodCount']
FoodMax = np.array(data["FoodMax"]) # ['FoodCount']
NutrientMin = np.array(data["NutrientMin"]) # ['NutrientCount']
NutrientMax = np.array(data["NutrientMax"]) # ['NutrientCount']
AmountNutrient = np.array(data["AmountNutrient"]) # ['FoodCount', 'NutrientCount']
AmountBought = model.addVars(FoodCount, vtype=gp.GRB.CONTINUOUS, name="AmountBought")

# Add minimum amount constraints for each food
for j in range(FoodCount):
    model.addConstr(AmountBought[j] >= FoodMin[j], name=f"min_amount_food_{j}")

# Add constraints to ensure the amount of food bought does not exceed the maximum allowable quantity
for j in range(FoodCount):
    model.addConstr(AmountBought[j] <= FoodMax[j], name=f"max_food_quantity_{j}")

# Add nutrient requirement constraints
for i in range(NutrientCount):
    model.addConstr(
        gp.quicksum(AmountBought[j] * AmountNutrient[j, i] for j in range(FoodCount)) >= NutrientMin[i],
        name=f"nutrient_requirement_{i}"
    )

# Add nutrient limits constraints
for i in range(NutrientCount):
    model.addConstr(
        gp.quicksum(AmountNutrient[j, i] * AmountBought[j] for j in range(FoodCount)) <= NutrientMax[i],
        name=f"nutrient_limit_{i}"
    )

# Add non-negativity constraints for food quantities  
for j in range(FoodCount):  
    model.addConstr(AmountBought[j] >= 0, name=f"non_negativity_food_{j}")

# Add nutritional intake constraints for each nutrient
for i in range(NutrientCount):
    model.addConstr(
        NutrientMin[i] <= gp.quicksum(AmountNutrient[j, i] * AmountBought[j] for j in range(FoodCount)),
        name=f"NutrientMin_constraint_{i}"
    )
    model.addConstr(
        gp.quicksum(AmountNutrient[j, i] * AmountBought[j] for j in range(FoodCount)) <= NutrientMax[i],
        name=f"NutrientMax_constraint_{i}"
    )

# Add constraints to ensure the quantity of each food purchased is within the specified minimum and maximum bounds
for j in range(FoodCount):
    model.addConstr(FoodMin[j] <= AmountBought[j], name=f"FoodMinConstraint_{j}")
    model.addConstr(AmountBought[j] <= FoodMax[j], name=f"FoodMaxConstraint_{j}")

# Set objective
model.setObjective(gp.quicksum(Cost[j] * AmountBought[j] for j in range(FoodCount)), gp.GRB.MINIMIZE)

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
