import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/dietu/data.json", "r") as f:
    data = json.load(f)

FoodNum = data["FoodNum"] # scalar parameter
NutrientNum = data["NutrientNum"] # scalar parameter
CostPerFood = np.array(data["CostPerFood"]) # ['FoodNum']
FoodMin = np.array(data["FoodMin"]) # ['FoodNum']
FoodMax = np.array(data["FoodMax"]) # ['FoodNum']
MinReqAmount = np.array(data["MinReqAmount"]) # ['NutrientNum']
MaxReqAmount = np.array(data["MaxReqAmount"]) # ['NutrientNum']
AmountPerNutrient = np.array(data["AmountPerNutrient"]) # ['FoodNum', 'NutrientNum']
FoodQuantity = model.addVars(FoodNum, vtype=gp.GRB.CONTINUOUS, name="FoodQuantity")

# Adding nutrient minimum requirement constraints
for i in range(NutrientNum):
    model.addConstr(
        gp.quicksum(AmountPerNutrient[j, i] * FoodQuantity[j] for j in range(FoodNum)) >= MinReqAmount[i],
        name=f"nutrient_min_req_{i}"
    )

# Add nutrient maximum requirement constraints
for i in range(NutrientNum):
    model.addConstr(
        gp.quicksum(FoodQuantity[j] * AmountPerNutrient[j, i] for j in range(FoodNum)) <= MaxReqAmount[i],
        name=f"nutrient_max_req_{i}"
    )

# Non-negativity constraints for food quantities
for j in range(FoodNum):
    model.addConstr(FoodQuantity[j] >= 0, name=f"NonNegativity_Food_{j}")

# Add constraints to ensure the selected quantity of each food item lies within the minimum and maximum bounds
for j in range(FoodNum):
    model.addConstr(FoodMin[j] <= FoodQuantity[j], name=f"FoodMinConstr_{j}")
    model.addConstr(FoodQuantity[j] <= FoodMax[j], name=f"FoodMaxConstr_{j}")

# Add nutrient balance constraints
for i in range(NutrientNum):
    model.addConstr(
        gp.quicksum(FoodQuantity[j] * AmountPerNutrient[j, i] for j in range(FoodNum)) >= MinReqAmount[i],
        name=f"nutrient_min_req_{i}"
    )
    model.addConstr(
        gp.quicksum(FoodQuantity[j] * AmountPerNutrient[j, i] for j in range(FoodNum)) <= MaxReqAmount[i],
        name=f"nutrient_max_req_{i}"
    )

# Add constraints for minimum and maximum food quantity limits
for j in range(FoodNum):
    model.addConstr(FoodQuantity[j] >= FoodMin[j], name=f"FoodMinConstr_{j}")
    model.addConstr(FoodQuantity[j] <= FoodMax[j], name=f"FoodMaxConstr_{j}")

# Set objective
model.setObjective(gp.quicksum(FoodQuantity[j] * CostPerFood[j] for j in range(FoodNum)), gp.GRB.MINIMIZE)

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
