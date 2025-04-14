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
ThinJars = model.addVar(vtype=gp.GRB.INTEGER, name="ThinJars")
StubbyJars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="StubbyJars")

# No code needed because the variable ThinJars has already been defined as an integer

StubbyJars.vtype = gp.GRB.INTEGER

# Add non-negativity constraint for ThinJars
model.addConstr(ThinJars >= 0, name="ThinJars_nonneg")

# Add non-negativity constraint for the number of stubby jars
model.addConstr(StubbyJars >= 0, name="nonnegativity_stubby_jars")

# Add constraint: Total shaping time for thin and stubby jars cannot exceed TotalShapingTime minutes per week
model.addConstr(ThinJars * ThinShapingTime + StubbyJars * StubbyShapingTime <= TotalShapingTime, name="shaping_time_limit")

# Total baking time constraint for thin and stubby jars
model.addConstr(ThinJars * ThinBakingTime + StubbyJars * StubbyBakingTime <= TotalBakingTime, "total_baking_time_constraint")

# Define objective function
model.setObjective(ProfitThin * ThinJars + ProfitStubby * StubbyJars, gp.GRB.MAXIMIZE)

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
