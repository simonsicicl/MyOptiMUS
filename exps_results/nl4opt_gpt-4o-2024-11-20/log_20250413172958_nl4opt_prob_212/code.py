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
PillsA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PillsA")
PillsB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PillsB")

# The variable PillsA is already defined. No additional code is needed for this constraint as non-negativity is implicitly handled by the domain of continuous variables in Gurobi.

# No additional code needed since the non-negativity constraint is inherently handled by the default lower bound (0) of the continuous variable PillsB during its definition.

# Add constraint for total units of iron from pills being at least IronReq
model.addConstr(IronA * PillsA + IronB * PillsB >= IronReq, name="iron_requirement")

# Add calcium requirement constraint
model.addConstr(PillsA * CalciumA + PillsB * CalciumB >= CalciumReq, name="calcium_requirement")

# Ensure the minimum iron requirement is met
model.addConstr(IronA * PillsA + IronB * PillsB >= IronReq, name="min_iron_requirement")

# Add constraint to ensure the minimum calcium requirement is met
model.addConstr(CalciumA * PillsA + CalciumB * PillsB >= CalciumReq, name="min_calcium_requirement")

# Set objective
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
