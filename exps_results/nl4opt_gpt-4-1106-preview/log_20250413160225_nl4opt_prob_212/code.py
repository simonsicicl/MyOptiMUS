import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_212/data.json", "r") as f:
    data = json.load(f)

IronA = data["IronA"] # scalar parameter
CalciumA = data["CalciumA"] # scalar parameter
IronB = data["IronB"] # scalar parameter
CalciumB = data["CalciumB"] # scalar parameter
IronReq = data["IronReq"] # scalar parameter
CalciumReq = data["CalciumReq"] # scalar parameter
CostA = data["CostA"] # scalar parameter
CostB = data["CostB"] # scalar parameter
PillsA = model.addVar(vtype=gp.GRB.INTEGER, name="PillsA")
PillsB = model.addVar(vtype=gp.GRB.INTEGER, name="PillsB")

# Add non-negativity constraint for the number of pills of supplement A
model.addConstr(PillsA >= 0, name="non_negativity_PillsA")

model.addConstr(PillsB >= 0, name="non_negativity_pillsB")

# Add constraint for minimum daily requirement of iron from pills
model.addConstr(IronA * PillsA + IronB * PillsB >= IronReq, name="min_daily_iron_requirement")

# Total units of calcium from pills must be at least the minimum daily requirement
model.addConstr(CalciumA * PillsA + CalciumB * PillsB >= CalciumReq, name="calcium_requirement")

# Ensure the minimum daily requirement of iron is met
model.addConstr(IronA * PillsA + IronB * PillsB >= IronReq, name="min_iron_requirement")

# Ensure the minimum daily requirement of calcium is met
model.addConstr(CalciumA * PillsA + CalciumB * PillsB >= CalciumReq, "min_calcium_requirement")

# Define the objective function
model.setObjective(CostA * PillsA + CostB * PillsB, gp.GRB.MINIMIZE)

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
