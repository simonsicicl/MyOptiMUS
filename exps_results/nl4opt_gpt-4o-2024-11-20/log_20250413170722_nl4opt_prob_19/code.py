import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_19/data.json", "r") as f:
    data = json.load(f)

ThinShapingTime = data["ThinShapingTime"] # scalar parameter
ThinBakingTime = data["ThinBakingTime"] # scalar parameter
StubbyShapingTime = data["StubbyShapingTime"] # scalar parameter
StubbyBakingTime = data["StubbyBakingTime"] # scalar parameter
TotalShapingTime = data["TotalShapingTime"] # scalar parameter
TotalBakingTime = data["TotalBakingTime"] # scalar parameter
ProfitThin = data["ProfitThin"] # scalar parameter
ProfitStubby = data["ProfitStubby"] # scalar parameter
ThinJarCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ThinJarCount")
StubbyJarCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="StubbyJarCount")

# Update variable ThinJarCount to integer type
ThinJarCount.vtype = gp.GRB.INTEGER

# Change StubbyJarCount's variable type from continuous to integer
StubbyJarCount.vtype = gp.GRB.INTEGER

# The variable ThinJarCount is already defined as non-negative. No additional code is required.

# Ensure the number of stubby jars produced is non-negative
model.addConstr(StubbyJarCount >= 0, name="non_negative_stubby_jars")

# Add total shaping time constraint for thin and stubby jars
model.addConstr(
    ThinShapingTime * ThinJarCount + StubbyShapingTime * StubbyJarCount <= TotalShapingTime,
    name="total_shaping_time"
)

# Add total baking time constraint for thin and stubby jars
model.addConstr(
    ThinBakingTime * ThinJarCount + StubbyBakingTime * StubbyJarCount <= TotalBakingTime,
    name="total_baking_time_constraint"
)

# Add shaping time constraint
model.addConstr(
    ThinShapingTime * ThinJarCount + StubbyShapingTime * StubbyJarCount <= TotalShapingTime,
    name="shaping_time_limit"
)

# Add constraint to ensure total baking time does not exceed available baking time
model.addConstr(ThinBakingTime * ThinJarCount + StubbyBakingTime * StubbyJarCount <= TotalBakingTime, name="baking_time_limit")

# The non-negativity of ThinJarCount is enforced by Gurobi's default non-negative domain for continuous variables. No additional constraint code is needed.

# No additional code needed since the variable "StubbyJarCount" is defined with non-negativity by default in Gurobi (continuous variables have a lower bound of 0 unless specified otherwise).

# Set objective
model.setObjective(ProfitThin * ThinJarCount + ProfitStubby * StubbyJarCount, gp.GRB.MAXIMIZE)

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
