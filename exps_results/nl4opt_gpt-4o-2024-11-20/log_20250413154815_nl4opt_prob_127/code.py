import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_127/data.json", "r") as f:
    data = json.load(f)

CaloriesAlmonds = data["CaloriesAlmonds"] # scalar parameter
ProteinAlmonds = data["ProteinAlmonds"] # scalar parameter
CaloriesCashews = data["CaloriesCashews"] # scalar parameter
ProteinCashews = data["ProteinCashews"] # scalar parameter
FatAlmonds = data["FatAlmonds"] # scalar parameter
FatCashews = data["FatCashews"] # scalar parameter
MinCalories = data["MinCalories"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
ServingsAlmonds = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsAlmonds")
ServingsCashews = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsCashews")

# No code is needed as the non-negativity is defined inherently by the lower bound of the ServingsAlmonds variable during variable definition (default lb=0).

# Ensure the number of servings of cashews is non-negative
model.addConstr(ServingsCashews >= 0, name="non_negative_servings_cashews")

# Add constraint ensuring the number of servings of almonds is at least twice the number of servings of cashews
model.addConstr(ServingsAlmonds >= 2 * ServingsCashews, name="almonds_cashews_ratio")

# Add calorie intake constraint
model.addConstr(
    ServingsAlmonds * CaloriesAlmonds + ServingsCashews * CaloriesCashews >= MinCalories,
    name="calorie_intake"
)

# Add total protein intake constraint
model.addConstr(
    ProteinAlmonds * ServingsAlmonds + ProteinCashews * ServingsCashews >= MinProtein,
    name="total_protein_constraint"
)

# Add calorie intake constraint
model.addConstr(
    ServingsAlmonds * CaloriesAlmonds + ServingsCashews * CaloriesCashews >= MinCalories,
    name="calorie_intake_constraint"
)

# Add total protein intake constraint
model.addConstr(ProteinAlmonds * ServingsAlmonds + ProteinCashews * ServingsCashews >= MinProtein, name="protein_requirement")

# Set objective
model.setObjective(FatAlmonds * ServingsAlmonds + FatCashews * ServingsCashews, gp.GRB.MINIMIZE)

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
