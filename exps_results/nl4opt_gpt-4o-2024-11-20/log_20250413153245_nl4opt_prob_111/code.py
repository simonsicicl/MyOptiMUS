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
CrabCakes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CrabCakes")
LobsterRolls = model.addVar(vtype=gp.GRB.CONTINUOUS, name="LobsterRolls")
TotalMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMeals")

# Add vitamin A intake constraint
model.addConstr(
    VitaminAcrab * CrabCakes + VitaminAlobster * LobsterRolls >= VitaminAmin,
    name="vitamin_A_minimum"
)

# Add vitamin C intake constraint
model.addConstr(
    VitaminCcrab * CrabCakes + VitaminClobster * LobsterRolls >= VitaminCmin,
    name="vitamin_c_intake"
)

# Add constraint linking LobsterRolls and CrabCakes based on LobsterFractionMax
model.addConstr((1 - LobsterFractionMax) * LobsterRolls <= LobsterFractionMax * CrabCakes, 
                name="lobster_fraction_constraint")

# The variable "CrabCakes" is already defined as non-negative due to its default non-negativity in Gurobi,
# so no additional constraint code is required.

# No code is needed because non-negativity is inherent to the LobsterRolls variable as it is defined with no negative allowance (vtype=gp.GRB.CONTINUOUS).

# Add Vitamin A minimum requirement constraint
model.addConstr(VitaminAcrab * CrabCakes + VitaminAlobster * LobsterRolls >= VitaminAmin, name="vitamin_a_requirement")

# Add Vitamin C minimum requirement constraint
model.addConstr(VitaminCcrab * CrabCakes + VitaminClobster * LobsterRolls >= VitaminCmin, name="vitamin_c_requirement")

# Add constraint to define TotalMeals as the sum of CrabCakes and LobsterRolls
model.addConstr(CrabCakes + LobsterRolls == TotalMeals, name="TotalMeals_Definition")

# Add constraint to limit the fraction of lobster rolls relative to total meals
model.addConstr(LobsterRolls <= LobsterFractionMax * TotalMeals, name="lobster_fraction_limit")

# Set objective
model.setObjective(FatCrab * CrabCakes + FatLobster * LobsterRolls, gp.GRB.MINIMIZE)

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
