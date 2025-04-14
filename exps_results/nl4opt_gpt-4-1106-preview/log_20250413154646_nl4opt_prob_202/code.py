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
NumberOfDesks = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfDesks")
NumberOfDrawers = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfDrawers")

# Ensure that the number of desks produced is non-negative
model.addConstr(NumberOfDesks >= 0, name="non_negative_desks")

# Add constraint to ensure the number of drawers is non-negative
model.addConstr(NumberOfDrawers >= 0, name="non_negative_drawers")

# Add constraint for the total assembly time for desks and drawers
model.addConstr(AssemblyDesk * NumberOfDesks + AssemblyDrawer * NumberOfDrawers <= TotalAssembly, name="Total_Assembly_Time")

# Add constraint for the total sanding time for desks and drawers
model.addConstr(SandingDesk * NumberOfDesks + SandingDrawer * NumberOfDrawers <= TotalSanding, name="sanding_time_limit")

# Assembly time constraint for desks and drawers
model.addConstr(NumberOfDesks * AssemblyDesk + NumberOfDrawers * AssemblyDrawer <= TotalAssembly, "assembly_time")

SandingDesk = data["SandingDesk"] # scalar parameter
SandingDrawer = data["SandingDrawer"] # scalar parameter
TotalSanding = data["TotalSanding"] # scalar parameter

model.addConstr(SandingDesk * NumberOfDesks + SandingDrawer * NumberOfDrawers <= TotalSanding, name="sanding_time_constraint")

# Define the objective function
model.setObjective(ProfitDesk * NumberOfDesks + ProfitDrawer * NumberOfDrawers, gp.GRB.MAXIMIZE)

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
