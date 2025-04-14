import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_209/data.json", "r") as f:
    data = json.load(f)

CalciumMin = data["CalciumMin"] # scalar parameter
VitaminMixMin = data["VitaminMixMin"] # scalar parameter
ProteinMin = data["ProteinMin"] # scalar parameter
CostRegular = data["CostRegular"] # scalar parameter
CostPremium = data["CostPremium"] # scalar parameter
CalciumRegular = data["CalciumRegular"] # scalar parameter
VitaminMixRegular = data["VitaminMixRegular"] # scalar parameter
ProteinRegular = data["ProteinRegular"] # scalar parameter
CalciumPremium = data["CalciumPremium"] # scalar parameter
VitaminMixPremium = data["VitaminMixPremium"] # scalar parameter
ProteinPremium = data["ProteinPremium"] # scalar parameter
BagsRegular = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BagsRegular")
BagsPremium = model.addVar(vtype=gp.GRB.CONTINUOUS, name="BagsPremium")

# Add calcium content constraint
model.addConstr(CalciumRegular * BagsRegular + CalciumPremium * BagsPremium >= CalciumMin, name="calcium_constraint")

# Add vitamin mix constraint
model.addConstr(
    VitaminMixRegular * BagsRegular + VitaminMixPremium * BagsPremium >= VitaminMixMin,
    name="vitamin_mix_constraint"
)

# Add protein minimum constraint
model.addConstr(ProteinRegular * BagsRegular + ProteinPremium * BagsPremium >= ProteinMin, name="protein_min_requirement")

# The non-negativity of BagsRegular is already enforced by defining it as a continuous variable, which is non-negative by default in Gurobi.

# Non-negativity constraint for premium brand bags
model.addConstr(BagsPremium >= 0, name="non_negativity_BagsPremium")

# Add calcium requirement constraint
model.addConstr(CalciumRegular * BagsRegular + CalciumPremium * BagsPremium >= CalciumMin, name="calcium_requirement")

# Add vitamin mix requirement constraint
model.addConstr(
    VitaminMixRegular * BagsRegular + VitaminMixPremium * BagsPremium >= VitaminMixMin,
    name="vitamin_mix_requirement"
)

# Add protein requirement constraint
model.addConstr(
    ProteinRegular * BagsRegular + ProteinPremium * BagsPremium >= ProteinMin,
    name="protein_requirement"
)

# Set objective
model.setObjective(CostRegular * BagsRegular + CostPremium * BagsPremium, gp.GRB.MINIMIZE)

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
