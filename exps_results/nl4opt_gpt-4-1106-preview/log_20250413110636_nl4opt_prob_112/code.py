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
NumDem1 = model.addVar(vtype=gp.GRB.INTEGER, name="NumDem1")
NumDem2 = model.addVar(vtype=gp.GRB.INTEGER, name="NumDem2")

# Add non-negativity constraint for the number of times Demonstration 1 is conducted
model.addConstr(NumDem1 >= 0, name="nonnegativity_NumDem1")

# Constraint to ensure the number of Demonstration 2 is non-negative
model.addConstr(NumDem2 >= 0, name="non_negativity_Dem2")

# Constraint: Total mint used in both demonstrations cannot exceed the available total mint
model.addConstr(NumDem1 * MintD1 + NumDem2 * MintD2 <= TotalMint, name="mint_usage_limit")

# Add constraint for total used units of active ingredient not to exceed TotalActive
model.addConstr(NumDem1 * ActiveD1 + NumDem2 * ActiveD2 <= TotalActive, name="total_active_ingredient")

# Black tar production constraint from Demonstration 1 and 2 should not exceed MaxTar
model.addConstr(NumDem1 * TarD1 + NumDem2 * TarD2 <= MaxTar, name="black_tar_production_limit")

# Constraint: The total usage of mint for all demonstrations does not exceed the total available units of mint
model.addConstr(MintD1 * NumDem1 + MintD2 * NumDem2 <= TotalMint, name="mint_usage")

# Add constraint for total usage of active ingredients
model.addConstr(ActiveD1 * NumDem1 + ActiveD2 * NumDem2 <= TotalActive, name="total_active_ingredient_usage")

# Black tar production constraint
model.addConstr(TarD1 * NumDem1 + TarD2 * NumDem2 <= MaxTar, name="max_black_tar")

# Set objective
model.setObjective(FoamD1 * NumDem1 + FoamD2 * NumDem2, gp.GRB.MAXIMIZE)

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
