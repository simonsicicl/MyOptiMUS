import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_111/data.json", "r") as f:
    data = json.load(f)

VitaminAmin = data["VitaminAmin"] # scalar parameter
VitaminCmin = data["VitaminCmin"] # scalar parameter
VitaminAcrab = data["VitaminAcrab"] # scalar parameter
VitaminCcrab = data["VitaminCcrab"] # scalar parameter
VitaminAlobster = data["VitaminAlobster"] # scalar parameter
VitaminClobster = data["VitaminClobster"] # scalar parameter
LobsterFractionMax = data["LobsterFractionMax"] # scalar parameter
FatCrab = data["FatCrab"] # scalar parameter
FatLobster = data["FatLobster"] # scalar parameter
NumberOfCrabCakes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCrabCakes")
NumberOfLobsterRolls = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLobsterRolls")

# Ensure the sailor consumes at least VitaminAmin units of vitamin A
model.addConstr(VitaminAcrab * NumberOfCrabCakes + VitaminAlobster * NumberOfLobsterRolls >= VitaminAmin, name="vitamin_A_minimum")

# Ensure the sailor consumes at least VitaminCmin units of vitamin C
model.addConstr(VitaminCcrab * NumberOfCrabCakes + VitaminClobster * NumberOfLobsterRolls >= VitaminCmin, name="vitamin_C_minimum")

# Constraint: Sailor can consume at most LobsterFractionMax percent of total meals as lobster rolls
model.addConstr(NumberOfLobsterRolls <= LobsterFractionMax * (NumberOfLobsterRolls + NumberOfCrabCakes), "max_lobster_fraction")

# Add constraint to ensure the number of crab cakes eaten is non-negative
model.addConstr(NumberOfCrabCakes >= 0, name="crab_cakes_non_negative")

# Add constraint to ensure the number of lobster rolls eaten is non-negative
model.addConstr(NumberOfLobsterRolls >= 0, name="lobster_rolls_non_negative")

# Define the objective function
model.setObjective(FatCrab * NumberOfCrabCakes + FatLobster * NumberOfLobsterRolls, gp.GRB.MINIMIZE)

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
