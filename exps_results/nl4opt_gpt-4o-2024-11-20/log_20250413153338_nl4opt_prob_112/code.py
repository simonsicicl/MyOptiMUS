import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_112/data.json", "r") as f:
    data = json.load(f)

MintD1 = data["MintD1"] # scalar parameter
MintD2 = data["MintD2"] # scalar parameter
ActiveD1 = data["ActiveD1"] # scalar parameter
ActiveD2 = data["ActiveD2"] # scalar parameter
FoamD1 = data["FoamD1"] # scalar parameter
FoamD2 = data["FoamD2"] # scalar parameter
TarD1 = data["TarD1"] # scalar parameter
TarD2 = data["TarD2"] # scalar parameter
TotalMint = data["TotalMint"] # scalar parameter
TotalActive = data["TotalActive"] # scalar parameter
MaxTar = data["MaxTar"] # scalar parameter
NumDemo1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumDemo1")
NumDemo2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumDemo2")

# The variable NumDemo1 is already non-negative due to its default properties (continuous variables in Gurobi are non-negative unless stated otherwise); no additional constraint is needed.

# Add non-negativity constraint for NumDemo2
model.addConstr(NumDemo2 >= 0, name="non_negativity_NumDemo2")

# Add constraint to ensure total mint usage for Demonstrations 1 and 2 does not exceed TotalMint
model.addConstr(MintD1 * NumDemo1 + MintD2 * NumDemo2 <= TotalMint, name="mint_usage_limit")

# Add constraint to ensure active ingredient usage does not exceed total available  
model.addConstr(ActiveD1 * NumDemo1 + ActiveD2 * NumDemo2 <= TotalActive, name="active_ingredient_limit")

# Add constraint for maximum allowable black tar production
model.addConstr(
    TarD1 * NumDemo1 + TarD2 * NumDemo2 <= MaxTar,
    name="max_black_tar_production"
)

# Add constraint to restrict total mint usage
model.addConstr(NumDemo1 * MintD1 + NumDemo2 * MintD2 <= TotalMint, name="mint_usage_limit")

# Add constraint to ensure active ingredient usage does not exceed the total available supply
model.addConstr(NumDemo1 * ActiveD1 + NumDemo2 * ActiveD2 <= TotalActive, name="active_ingredient_usage")

# Add constraint for the total amount of black tar produced
model.addConstr(NumDemo1 * TarD1 + NumDemo2 * TarD2 <= MaxTar, name="max_black_tar")

# No need for additional code to set non-negativity as it is already implicit in the variable definitions with Gurobi's default lower bound (0).

# Set objective
model.setObjective(FoamD1 * NumDemo1 + FoamD2 * NumDemo2, gp.GRB.MAXIMIZE)

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
