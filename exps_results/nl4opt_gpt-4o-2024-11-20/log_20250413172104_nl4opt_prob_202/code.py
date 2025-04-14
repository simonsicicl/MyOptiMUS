import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_202/data.json", "r") as f:
    data = json.load(f)

AssemblyDesk = data["AssemblyDesk"] # scalar parameter
SandingDesk = data["SandingDesk"] # scalar parameter
AssemblyDrawer = data["AssemblyDrawer"] # scalar parameter
SandingDrawer = data["SandingDrawer"] # scalar parameter
TotalAssembly = data["TotalAssembly"] # scalar parameter
TotalSanding = data["TotalSanding"] # scalar parameter
ProfitDesk = data["ProfitDesk"] # scalar parameter
ProfitDrawer = data["ProfitDrawer"] # scalar parameter
NumDesks = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumDesks")
NumDrawers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumDrawers")

# Non-negativity constraints to ensure production values are non-negative
model.addConstr(NumDesks >= 0, name="non_negativity_NumDesks")
model.addConstr(NumDrawers >= 0, name="non_negativity_NumDrawers")

# The non-negativity of NumDrawers is enforced implicitly by setting the lower bound of the variable to 0.

# Add assembly time constraint
model.addConstr(
    NumDesks * AssemblyDesk + NumDrawers * AssemblyDrawer <= TotalAssembly,
    name="assembly_time_constraint"
)

# Add sanding time constraint
model.addConstr((SandingDesk * NumDesks) + (SandingDrawer * NumDrawers) <= TotalSanding, name="sanding_time_limit")

# Add assembly time constraint
model.addConstr(NumDesks * AssemblyDesk + NumDrawers * AssemblyDrawer <= TotalAssembly, name="assembly_time_constraint")

# Add sanding time constraint
model.addConstr(SandingDesk * NumDesks + SandingDrawer * NumDrawers <= TotalSanding, name="sanding_time_constraint")

# Set objective
model.setObjective(ProfitDesk * NumDesks + ProfitDrawer * NumDrawers, gp.GRB.MAXIMIZE)

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
