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

# Add non-negativity constraint for servings of almonds
model.addConstr(ServingsAlmonds >= 0, name="nonnegativity_servings_almonds")

# Since ServingsCashews has already been defined as a continuous variable, 
# we just need to add a constraint to ensure it is non-negative.
model.addConstr(ServingsCashews >= 0, name="non_negativity_cashews")

model.addConstr(ServingsAlmonds >= 2 * ServingsCashews, name="almonds_cashews_ratio")

# Add constraint for minimum total calorie intake from almonds and cashews
model.addConstr(ServingsAlmonds * CaloriesAlmonds + ServingsCashews * CaloriesCashews >= MinCalories, name="min_calories_intake")

# Ensure total protein intake from almonds and cashews is at least the minimum required
model.addConstr(ProteinAlmonds * ServingsAlmonds + ProteinCashews * ServingsCashews >= MinProtein, "min_protein_intake")

# Ensure the total calories from almonds and cashews meet the minimum requirement
model.addConstr(CaloriesAlmonds * ServingsAlmonds + CaloriesCashews * ServingsCashews >= MinCalories, 
                name="min_calories_constraint")

# Ensure the total protein from almonds and cashews meet the minimum requirement
model.addConstr(ProteinAlmonds * ServingsAlmonds + ProteinCashews * ServingsCashews >= MinProtein, name="min_protein_requirement")

# Define the objective function
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
