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
CleansingUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CleansingUsed")
OdorRemovingUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OdorRemovingUsed")

# Add constraint ensuring the amount of cleansing chemical used is at least MinCleansing
model.addConstr(CleansingUsed >= MinCleansing, name="min_cleansing_constraint")

# Add constraint for the total amount of chemicals used per house
model.addConstr(CleansingUsed + OdorRemovingUsed <= MaxTotal, name="chemical_usage_limit")

# Add constraint: The amount of cleansing chemical cannot exceed MaxRatio times the amount of odor-removing chemical
model.addConstr(CleansingUsed <= MaxRatio * OdorRemovingUsed, name="cleansing_chemical_limit")

# The constraint is already satisfied as CleansingUsed was defined as a continuous variable, ensuring non-negativity.

# OdorRemovingUsed is already defined as a continuous variable, ensuring non-negativity. No additional code needed.

# Add constraint to ensure the minimum units of cleansing chemical is used
model.addConstr(CleansingUsed >= MinCleansing, name="min_cleansing_requirement")

# Add constraint to ensure total chemicals used per house does not exceed maximum allowed
model.addConstr(CleansingUsed + OdorRemovingUsed <= MaxTotal, name="total_chemicals_limit")

# Add constraint to ensure cleansing chemical does not exceed the maximum ratio relative to odor-removing chemical
model.addConstr(CleansingUsed <= MaxRatio * OdorRemovingUsed, name="cleansing_ratio_constraint")

# The variable "CleansingUsed" is non-negative by default (continuous variables in Gurobi are non-negative), so no additional constraint is needed.

# No code needed, as non-negativity is inherent to the variable type (GRB.CONTINUOUS); this constraint is automatically satisfied.

# Set objective
model.setObjective(Tc * CleansingUsed + To * OdorRemovingUsed, gp.GRB.MINIMIZE)

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
