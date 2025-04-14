import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_17/data.json", "r") as f:
    data = json.load(f)

ProfitChair = data["ProfitChair"] # scalar parameter
ProfitDresser = data["ProfitDresser"] # scalar parameter
TotalStain = data["TotalStain"] # scalar parameter
TotalOak = data["TotalOak"] # scalar parameter
StainPerChair = data["StainPerChair"] # scalar parameter
OakPerChair = data["OakPerChair"] # scalar parameter
StainPerDresser = data["StainPerDresser"] # scalar parameter
OakPerDresser = data["OakPerDresser"] # scalar parameter
NumberOfChairs = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfChairs")
NumberOfDressers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfDressers")
TotalStainUsedByDressers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalStainUsedByDressers")
TotalOakUsedByDressers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalOakUsedByDressers")

# Change integrality of the variable to ensure NumberOfChairs is an integer
NumberOfChairs.vtype = gp.GRB.INTEGER

# Ensure the variable 'NumberOfDressers' is an integer
NumberOfDressers.vtype = gp.GRB.INTEGER

# Number of chairs must be non-negative
model.addConstr(NumberOfChairs >= 0, name="non_negative_chairs_constraint")

# No code needed, as non-negativity is inherent to the variable type (CONTINUOUS in gurobipy)

# Add constraint for total stain usage
model.addConstr(StainPerChair * NumberOfChairs + StainPerDresser * NumberOfDressers <= TotalStain, name="stain_usage_limit")

# Add constraint for total oak wood usage
model.addConstr(
    NumberOfChairs * OakPerChair + NumberOfDressers * OakPerDresser <= TotalOak,
    name="total_oak_usage"
)

# Add constraint for stain availability
model.addConstr(
    NumberOfChairs * StainPerChair + NumberOfDressers * StainPerDresser <= TotalStain,
    name="stain_availability"
)

# Constraint enforcing the relationship between total stain used and the number of dressers produced
TotalStainUsedByDressers = NumberOfDressers * StainPerDresser

# Add oak wood usage constraint
model.addConstr(OakPerChair * NumberOfChairs + OakPerDresser * NumberOfDressers <= TotalOak, name="oak_wood_limit")

# Add constraint for oak wood usage by dressers
model.addConstr(TotalOakUsedByDressers <= TotalOak, name="oak_wood_usage_constraint")

# No additional code needed since the variable "NumberOfDressers" is defined with non-negativity by default in Gurobi (continuous variables have a non-negative domain unless specified otherwise).

# Add equality constraint for TotalOakUsedByDressers
model.addConstr(TotalOakUsedByDressers == NumberOfDressers * OakPerDresser, name="oak_wood_dresser_constraint")

# Add stain availability constraint
model.addConstr(StainPerChair * NumberOfChairs + StainPerDresser * NumberOfDressers <= TotalStain, name="stain_availability")

# Add constraint to limit the total oak wood usage
model.addConstr(OakPerChair * NumberOfChairs + OakPerDresser * NumberOfDressers <= TotalOak, name="oak_wood_limit")

# Set objective
model.setObjective(ProfitChair * NumberOfChairs + ProfitDresser * NumberOfDressers, gp.GRB.MAXIMIZE)

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
