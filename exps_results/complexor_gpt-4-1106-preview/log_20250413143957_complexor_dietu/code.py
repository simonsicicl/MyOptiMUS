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
x = model.addVars(FoodNum, vtype=gp.GRB.CONTINUOUS, name="x")

# Minimum required amount of each nutrient constraints
for i in range(NutrientNum):
    model.addConstr(gp.quicksum(AmountPerNutrient[j, i] * x[j] for j in range(FoodNum)) >= MinReqAmount[i], 
                    name="nutrient_min_requirement_"+str(i))

# Add nutrient maximum constraints
for i in range(NutrientNum):
    model.addConstr(gp.quicksum(AmountPerNutrient[j, i] * x[j] for j in range(FoodNum)) <= MaxReqAmount[i], name=f"nutrient_max_{i}")

# Add non-negativity constraints for each food item
for j in range(FoodNum):
    model.addConstr(x[j] >= 0, name=f"non_negativity_{j}")

# Set objective
model.setObjective(gp.quicksum(CostPerFood[i] * x[i] for i in range(FoodNum)), gp.GRB.MINIMIZE)

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
