import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_84/data.json", "r") as f:
    data = json.load(f)

MetalAlpha = data["MetalAlpha"] # scalar parameter
AcidAlpha = data["AcidAlpha"] # scalar parameter
ElectricityAlpha = data["ElectricityAlpha"] # scalar parameter
MetalBeta = data["MetalBeta"] # scalar parameter
AcidBeta = data["AcidBeta"] # scalar parameter
ElectricityBeta = data["ElectricityBeta"] # scalar parameter
TotalMetal = data["TotalMetal"] # scalar parameter
TotalAcid = data["TotalAcid"] # scalar parameter
NumAlphaExperiments = model.addVar(vtype=gp.GRB.INTEGER, name="NumAlphaExperiments")
NumBetaExperiments = model.addVar(vtype=gp.GRB.INTEGER, name="NumBetaExperiments")

# Since NumAlphaExperiments is already defined as an integer variable, we just need to add a constraint to ensure it is non-negative
model.addConstr(NumAlphaExperiments >= 0, name="non_negative_alpha_experiments")

# Since NumBetaExperiments is already defined as an integer variable, no code is needed to enforce non-negativity.
# The Gurobi solver enforces that integer variables are non-negative by default, hence no additional constraint is necessary.

# Add constraint: Total metal consumed by alpha and beta experiments is less than or equal to the total metal available
model.addConstr(MetalAlpha * NumAlphaExperiments + MetalBeta * NumBetaExperiments <= TotalMetal, 
                name="total_metal_consumption")

# Acid consumption constraint
model.addConstr(AcidAlpha * NumAlphaExperiments + AcidBeta * NumBetaExperiments <= TotalAcid, name="total_acid_constraint")

# Define objective function
model.setObjective(ElectricityAlpha * NumAlphaExperiments + ElectricityBeta * NumBetaExperiments, gp.GRB.MAXIMIZE)

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
