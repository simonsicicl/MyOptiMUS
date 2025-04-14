import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_105/data.json", "r") as f:
    data = json.load(f)

Tc = data["Tc"] # scalar parameter
To = data["To"] # scalar parameter
MinCleansing = data["MinCleansing"] # scalar parameter
MaxTotal = data["MaxTotal"] # scalar parameter
MaxRatio = data["MaxRatio"] # scalar parameter
CleansingChemicalUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CleansingChemicalUsed")
OdorRemovingChemicalUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OdorRemovingChemicalUsed")

# Ensure the amount of cleansing chemical used is at least the minimum required
model.addConstr(CleansingChemicalUsed >= MinCleansing, name="min_cleansing_requirement")

# Add constraint for the maximum amount of chemicals used per house
model.addConstr(CleansingChemicalUsed + OdorRemovingChemicalUsed <= MaxTotal, "chemical_usage_limit")

# Add constraint: Cleansing chemical used cannot exceed the maximum ratio times the amount of odor-removing chemical used
model.addConstr(CleansingChemicalUsed <= MaxRatio * OdorRemovingChemicalUsed, name="chemical_use_ratio")

# Add constraint for non-negativity of the amount of cleansing chemical used
model.addConstr(CleansingChemicalUsed >= 0, name="cleansing_chemical_non_negative")

# The amount of odor-removing chemical used is non-negative
model.addConstr(OdorRemovingChemicalUsed >= 0, "nonnegativity_OdorRemovingChemicalUsed")

# Ensure the minimum amount of cleansing chemical is used
model.addConstr(CleansingChemicalUsed >= MinCleansing, name="min_cleansing_requirement")

# Add constraint for the maximum amount of chemicals used per house
model.addConstr(CleansingChemicalUsed + OdorRemovingChemicalUsed <= MaxTotal, name="Max_Chemicals_Per_House")

# Add constraint for the maximum ratio of cleansing chemical to odor-removing chemical
model.addConstr(CleansingChemicalUsed <= MaxRatio * OdorRemovingChemicalUsed, "ratio_constraint")

# Set objective
model.setObjective(-(CleansingChemicalUsed * Tc + OdorRemovingChemicalUsed * To), gp.GRB.MINIMIZE)

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
