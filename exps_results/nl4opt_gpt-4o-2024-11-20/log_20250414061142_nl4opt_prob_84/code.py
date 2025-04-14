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
AlphaExperiments = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AlphaExperiments")
BetaExperiments = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BetaExperiments")

# The non-negativity constraint for AlphaExperiments is implicitly satisfied by the variable's bounds (default lower bound is 0 for continuous variables in Gurobi).

# Non-negativity constraint for BetaExperiments
model.addConstr(BetaExperiments >= 0, name="non_negative_beta_experiments")

# Add constraint ensuring total metal consumption does not exceed available metal
model.addConstr(
    MetalAlpha * AlphaExperiments + MetalBeta * BetaExperiments <= TotalMetal,
    name="metal_consumption"
)

# Add constraint to ensure total acid consumption does not exceed available total acid
model.addConstr(
    (AcidAlpha * AlphaExperiments) + (AcidBeta * BetaExperiments) <= TotalAcid,
    name="acid_consumption_limit"
)

# Add metal usage constraint
model.addConstr(MetalAlpha * AlphaExperiments + MetalBeta * BetaExperiments <= TotalMetal, name="metal_constraint")

# Add acid usage constraint
model.addConstr(
    AlphaExperiments * AcidAlpha + BetaExperiments * AcidBeta <= TotalAcid,
    name="acid_constraint"
)

# Add non-negativity constraint for AlphaExperiments
model.addConstr(AlphaExperiments >= 0, name="non_negativity_AlphaExperiments")

# Add non-negativity constraint for BetaExperiments
model.addConstr(BetaExperiments >= 0, name="non_negativity_BetaExperiments")

# Set objective
model.setObjective(AlphaExperiments * ElectricityAlpha + BetaExperiments * ElectricityBeta, gp.GRB.MAXIMIZE)

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
