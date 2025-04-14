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
NumberOfCheapBoxes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCheapBoxes")
NumberOfExpensiveBoxes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfExpensiveBoxes")

# Since the variable "NumberOfCheapBoxes" is already defined as non-negative (default lower bound is 0 for continuous variables in Gurobi), no additional constraint is needed.

# Add non-negativity constraint for NumberOfExpensiveBoxes
model.addConstr(NumberOfExpensiveBoxes >= 0, name="non_negative_expensive_boxes")

# Add constraint to ensure total metal usage does not exceed available metal
model.addConstr(
    MetalCheap * NumberOfCheapBoxes + MetalExpensive * NumberOfExpensiveBoxes <= MetalTotal,
    name="total_metal_limit"
)

# Add acid usage constraint
model.addConstr(
    AcidCheap * NumberOfCheapBoxes + AcidExpensive * NumberOfExpensiveBoxes <= AcidTotal, 
    name="acid_usage_constraint"
)

# Add heat generation constraint
model.addConstr(
    NumberOfCheapBoxes * HeatCheap + NumberOfExpensiveBoxes * HeatExpensive <= HeatMax,
    name="heat_generation_constraint"
)

# Add metal usage constraint
model.addConstr(NumberOfCheapBoxes * MetalCheap + NumberOfExpensiveBoxes * MetalExpensive <= MetalTotal, name="metal_usage")

# Add acid usage constraint
model.addConstr(AcidCheap * NumberOfCheapBoxes + AcidExpensive * NumberOfExpensiveBoxes <= AcidTotal, name="acid_usage_constraint")

# Add heat production constraint
model.addConstr(
    NumberOfCheapBoxes * HeatCheap + NumberOfExpensiveBoxes * HeatExpensive <= HeatMax,
    name="heat_production_constraint"
)

# Set objective
model.setObjective(FoamCheap * NumberOfCheapBoxes + FoamExpensive * NumberOfExpensiveBoxes, gp.GRB.MAXIMIZE)

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
