import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_222/data.json", "r") as f:
    data = json.load(f)

StrawberryProfit = data["StrawberryProfit"] # scalar parameter
SugarProfit = data["SugarProfit"] # scalar parameter
MaxStrawberryDemand = data["MaxStrawberryDemand"] # scalar parameter
MaxSugarDemand = data["MaxSugarDemand"] # scalar parameter
MaxProductionCapacity = data["MaxProductionCapacity"] # scalar parameter
x1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="x1")
x2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="x2")

# Constraint: Number of strawberry cookies produced must be non-negative
model.addConstr(x1 >= 0, "strawberry_cookies_nonnegativity")

# The number of sugar cookies produced must be non-negative
model.addConstr(x2 >= 0, name="sugar_cookies_nonnegativity")

# Constraint for maximum strawberry cookies demand per day
model.addConstr(x1 <= MaxStrawberryDemand, name="max_strawberry_demand")

# Constraint for maximum daily sugar cookie demand
model.addConstr(x2 <= MaxSugarDemand, name="max_sugar_demand")

# Add constraint: total number of strawberry and sugar cookies produced must not exceed daily maximum production capacity
model.addConstr(x1 + x2 <= MaxProductionCapacity, "max_production_capacity")

model.addConstr(x1 + x2 <= MaxProductionCapacity, name="max_production_capacity")

model.addConstr(x1 <= MaxStrawberryDemand, name="max_strawberry_demand")

# Add maximum sugar cookie demand constraint
model.addConstr(x2 <= MaxSugarDemand, name="max_sugar_demand")

# Set objective
model.setObjective(StrawberryProfit * x1 + SugarProfit * x2, gp.GRB.MAXIMIZE)

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
