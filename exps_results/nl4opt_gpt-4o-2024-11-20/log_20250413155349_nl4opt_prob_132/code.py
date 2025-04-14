import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_132/data.json", "r") as f:
    data = json.load(f)

Powder1 = data["Powder1"] # scalar parameter
Glue1 = data["Glue1"] # scalar parameter
Slime1 = data["Slime1"] # scalar parameter
Powder2 = data["Powder2"] # scalar parameter
Glue2 = data["Glue2"] # scalar parameter
Slime2 = data["Slime2"] # scalar parameter
Mess1 = data["Mess1"] # scalar parameter
Mess2 = data["Mess2"] # scalar parameter
TotalPowder = data["TotalPowder"] # scalar parameter
TotalGlue = data["TotalGlue"] # scalar parameter
MaxMess = data["MaxMess"] # scalar parameter
Table1Setups = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Table1Setups")
Table2Setups = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Table2Setups")

# Since Table1Setups was defined as a continuous variable, it is already non-negative by default in Gurobi.
# No additional constraint is needed.

# The non-negativity of Table2Setups is inherent due to its default non-negative domain as a continuous variable,
# so no constraint code is needed.

# Add powder usage constraint
model.addConstr(
    Powder1 * Table1Setups + Powder2 * Table2Setups <= TotalPowder, 
    name="powder_usage_constraint"
)

# Add constraint for glue usage by Table 1 and Table 2
model.addConstr(Glue1 * Table1Setups + Glue2 * Table2Setups <= TotalGlue, name="glue_usage_constraint")

# Add mess production constraint for tables
model.addConstr(Mess1 * Table1Setups + Mess2 * Table2Setups <= MaxMess, name="mess_limit")

# Add total powder usage constraint
model.addConstr(Powder1 * Table1Setups + Powder2 * Table2Setups <= TotalPowder, name="total_powder_usage")

# Add glue usage constraint
model.addConstr(Glue1 * Table1Setups + Glue2 * Table2Setups <= TotalGlue, name="glue_usage_constraint")

# Add constraint to ensure total mess produced does not exceed the maximum allowable mess
model.addConstr(Mess1 * Table1Setups + Mess2 * Table2Setups <= MaxMess, name="mess_limit")

# The non-negativity of Table1Setups is inherent due to its type being continuous and it starts as 0 by default.
# No additional constraint is needed.

# The non-negativity of Table2Setups is inherent due to its type being CONTINUOUS in gurobipy
# No additional code required to enforce the constraint: Table2Setups >= 0

# Set objective
model.setObjective(Slime1 * Table1Setups + Slime2 * Table2Setups, gp.GRB.MAXIMIZE)

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
