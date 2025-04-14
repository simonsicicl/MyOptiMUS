import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_205/data.json", "r") as f:
    data = json.load(f)

CostNoodles = data["CostNoodles"] # scalar parameter
CaloriesNoodles = data["CaloriesNoodles"] # scalar parameter
ProteinNoodles = data["ProteinNoodles"] # scalar parameter
CostBars = data["CostBars"] # scalar parameter
CaloriesBars = data["CaloriesBars"] # scalar parameter
ProteinBars = data["ProteinBars"] # scalar parameter
MinCalories = data["MinCalories"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
ServingsNoodles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsNoodles")
ServingsBars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsBars")

# Add calorie intake constraint
model.addConstr(CaloriesNoodles * ServingsNoodles + CaloriesBars * ServingsBars >= MinCalories, name="calorie_intake")

# Add total protein constraint
model.addConstr(
    ServingsNoodles * ProteinNoodles + ServingsBars * ProteinBars >= MinProtein,
    name="total_protein_constraint"
)

# The variable "ServingsNoodles" is non-negative due to its default lower bound (0) in Gurobi. No additional constraint is needed.

# Non-negativity constraint for ServingsBars
model.addConstr(ServingsBars >= 0, name="non_negativity_ServingsBars")

# Non-negativity constraint for ServingsBars
model.addConstr(ServingsBars >= 0, name="non_negativity_ServingsBars")

# Add total calorie intake constraint
model.addConstr(ServingsNoodles * CaloriesNoodles + ServingsBars * CaloriesBars >= MinCalories, name="calorie_intake_constraint")

# Add protein intake constraint
model.addConstr(ProteinNoodles * ServingsNoodles + ProteinBars * ServingsBars >= MinProtein, name="protein_intake")

# The variable "ServingsNoodles" is non-negative due to its default lower bound (0) in Gurobi's `addVar`.

# Non-negativity constraint for ServingsBars is implicitly ensured by the variable's defined lower bound (default is 0).

# Set objective
model.setObjective(CostNoodles * ServingsNoodles + CostBars * ServingsBars, gp.GRB.MINIMIZE)

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
