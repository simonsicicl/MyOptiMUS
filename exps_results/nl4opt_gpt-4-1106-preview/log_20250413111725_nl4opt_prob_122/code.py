import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_122/data.json", "r") as f:
    data = json.load(f)

MetalCheap = data["MetalCheap"] # scalar parameter
AcidCheap = data["AcidCheap"] # scalar parameter
FoamCheap = data["FoamCheap"] # scalar parameter
MetalExpensive = data["MetalExpensive"] # scalar parameter
AcidExpensive = data["AcidExpensive"] # scalar parameter
FoamExpensive = data["FoamExpensive"] # scalar parameter
HeatCheap = data["HeatCheap"] # scalar parameter
HeatExpensive = data["HeatExpensive"] # scalar parameter
MetalTotal = data["MetalTotal"] # scalar parameter
AcidTotal = data["AcidTotal"] # scalar parameter
HeatMax = data["HeatMax"] # scalar parameter
CheapBoxes = model.addVar(vtype=gp.GRB.INTEGER, name="CheapBoxes")
ExpensiveBoxes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ExpensiveBoxes")

# Add constraint to ensure the number of cheap boxes is non-negative
model.addConstr(CheapBoxes >= 0, name="non_negativity_CheapBoxes")

# Add constraint: Number of expensive boxes should be non-negative
model.addConstr(ExpensiveBoxes >= 0, name="expensive_boxes_non_negative")

# Total metal usage constraint
model.addConstr(MetalCheap * CheapBoxes + MetalExpensive * ExpensiveBoxes <= MetalTotal, name="TotalMetalConstraint")

# Constraint: Total acid used for both cheap and expensive boxes must not exceed the total available acid
model.addConstr(AcidCheap * CheapBoxes + AcidExpensive * ExpensiveBoxes <= AcidTotal, name="acid_usage")

# Total heat from production constraint
model.addConstr(HeatCheap * CheapBoxes + HeatExpensive * ExpensiveBoxes <= HeatMax, name="heat_limit")

# Define the objective function
model.setObjective(CheapBoxes * FoamCheap + ExpensiveBoxes * FoamExpensive, gp.GRB.MAXIMIZE)

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
