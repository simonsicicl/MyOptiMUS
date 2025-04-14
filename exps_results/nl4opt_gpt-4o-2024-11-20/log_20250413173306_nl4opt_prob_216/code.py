import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_216/data.json", "r") as f:
    data = json.load(f)

TotalBatter = data["TotalBatter"] # scalar parameter
TotalMilk = data["TotalMilk"] # scalar parameter
BatterCrepe = data["BatterCrepe"] # scalar parameter
MilkCrepe = data["MilkCrepe"] # scalar parameter
BatterSponge = data["BatterSponge"] # scalar parameter
MilkSponge = data["MilkSponge"] # scalar parameter
BatterBirthday = data["BatterBirthday"] # scalar parameter
MilkBirthday = data["MilkBirthday"] # scalar parameter
ProfitCrepe = data["ProfitCrepe"] # scalar parameter
ProfitSponge = data["ProfitSponge"] # scalar parameter
ProfitBirthday = data["ProfitBirthday"] # scalar parameter
CrepeCakes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CrepeCakes")
SpongeCakes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SpongeCakes")
BirthdayCakes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BirthdayCakes")

# Non-negativity constraint for CrepeCakes
model.addConstr(CrepeCakes >= 0, name="non_negativity_CrepeCakes")

# The variable "SpongeCakes" is non-negative by default since it is a continuous variable.

# The variable "BirthdayCakes" already has the specified constraint (non-negativity) because variables in Gurobi are non-negative by default.

# Add constraint for the total batter usage
model.addConstr(
    CrepeCakes * BatterCrepe + SpongeCakes * BatterSponge + BirthdayCakes * BatterBirthday <= TotalBatter,
    name="total_batter_usage"
)

# Add constraint to ensure total milk usage does not exceed TotalMilk
model.addConstr(
    MilkCrepe * CrepeCakes + MilkSponge * SpongeCakes + MilkBirthday * BirthdayCakes <= TotalMilk,
    name="milk_usage_constraint"
)

# Add constraint for total batter used not exceeding the available batter  
model.addConstr(  
    CrepeCakes * BatterCrepe + SpongeCakes * BatterSponge + BirthdayCakes * BatterBirthday <= TotalBatter,  
    name="batter_limit"  
)

# Add milk constraint to ensure total usage doesn't exceed available milk
model.addConstr(
    MilkCrepe * CrepeCakes + MilkSponge * SpongeCakes + MilkBirthday * BirthdayCakes <= TotalMilk,
    name="milk_constraint"
)

# Set objective
model.setObjective(ProfitCrepe * CrepeCakes + ProfitSponge * SpongeCakes + ProfitBirthday * BirthdayCakes, gp.GRB.MAXIMIZE)

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
