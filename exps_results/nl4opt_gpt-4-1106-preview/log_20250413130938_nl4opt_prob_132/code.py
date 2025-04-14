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
Table1Setups = model.addVar(vtype=gp.GRB.INTEGER, name="Table1Setups")
Table2Setups = model.addVar(vtype=gp.GRB.INTEGER, name="Table2Setups")

model.addConstr(Table1Setups >= 0, name="non_negative_setups")

# Add non-negativity constraint for the number of Table 2 setups
model.addConstr(Table2Setups >= 0, name="non_negativity_Table2Setups")

# Add constraint for total quantity of powder used by Table 1 and Table 2
model.addConstr(Powder1 * Table1Setups + Powder2 * Table2Setups <= TotalPowder, name="powder_usage")

GlueConstraint = model.addConstr(Glue1 * Table1Setups + Glue2 * Table2Setups <= TotalGlue, name="GlueUsageConstraint")

# Total mess produced by Table 1 and Table 2 setups does not exceed MaxMess
model.addConstr(Mess1 * Table1Setups + Mess2 * Table2Setups <= MaxMess, name="max_mess_constraint")

# Define the objective function
objective = Slime1 * Table1Setups + Slime2 * Table2Setups

# Set the objective
model.setObjective(objective, gp.GRB.MAXIMIZE)

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
