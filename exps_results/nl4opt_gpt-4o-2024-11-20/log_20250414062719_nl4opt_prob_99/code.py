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
CherryPacks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CherryPacks")

# The non-negativity of PeachPacks is automatically ensured due to its default non-negative domain in Gurobi,
# so no constraint code is needed.

# No additional code needed since the variable "CherryPacks" is already defined with non-negativity (default domain for continuous variables in Gurobi).

# Add constraint ensuring total peach flavoring used does not exceed available total units
model.addConstr(PeachPacks * PeachRequirement <= TotalPeach, name="peach_flavoring_limit")

# Add constraint to ensure total cherry flavoring used does not exceed available TotalCherry
model.addConstr(CherryRequirement * CherryPacks <= TotalCherry, name="cherry_flavoring_limit")

# Add constraint: The number of peach candy packs must be greater than the number of cherry candy packs
model.addConstr(PeachPacks >= CherryPacks + 1, name="PeachVsCherry")

# Add constraint ensuring minimum cherry percentage
model.addConstr(CherryPacks - MinimumCherryPercentage * (CherryPacks + PeachPacks) >= 0, name="min_cherry_percentage")

# Add constraint for peach flavoring usage
model.addConstr(PeachRequirement * PeachPacks <= TotalPeach, name="peach_flavoring_limit")

# Add constraint to ensure total cherry flavoring used does not exceed available amount
model.addConstr(CherryPacks * CherryRequirement <= TotalCherry, name="cherry_flavoring_limit")

# Add minimum cherry percentage constraint
model.addConstr(CherryPacks >= MinimumCherryPercentage * (PeachPacks + CherryPacks), name="min_cherry_percentage")

# Set objective
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
