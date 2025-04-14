import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_99/data.json", "r") as f:
    data = json.load(f)

PeachRequirement = data["PeachRequirement"] # scalar parameter
PeachSyrup = data["PeachSyrup"] # scalar parameter
CherryRequirement = data["CherryRequirement"] # scalar parameter
CherrySyrup = data["CherrySyrup"] # scalar parameter
TotalPeach = data["TotalPeach"] # scalar parameter
TotalCherry = data["TotalCherry"] # scalar parameter
MinimumCherryPercentage = data["MinimumCherryPercentage"] # scalar parameter
PeachPacks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PeachPacks")
CherryPacks = model.addVar(vtype=gp.GRB.INTEGER, name="CherryPacks")

# Add non-negativity constraint for peach flavored candy packs
model.addConstr(PeachPacks >= 0, name="peach_packs_nonnegativity")

model.addConstr(CherryPacks >= 0, "CherryPacks_nonnegativity")

# Constraint: Total used peach flavoring cannot exceed the total available units of peach flavoring
model.addConstr(PeachRequirement * PeachPacks <= TotalPeach, name="peach_flavoring_limit")

# Constraint to ensure total used cherry flavoring does not exceed total available units
model.addConstr(CherryRequirement * CherryPacks <= TotalCherry, name="cherry_flavoring_limit")

# Ensure the number of peach candy packs is greater than the number of cherry candy packs
model.addConstr(PeachPacks >= CherryPacks + 1, name="peach_cherry_relation")

# At least MinimumCherryPercentage of the packs must be cherry flavored
model.addConstr(CherryPacks >= MinimumCherryPercentage * (PeachPacks + CherryPacks), name="CherryPacks_Minimum_Percentage")

# Define the objective function
model.setObjective(PeachSyrup * PeachPacks + CherrySyrup * CherryPacks, gp.GRB.MINIMIZE)

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
