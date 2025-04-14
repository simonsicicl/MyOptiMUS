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
RegularBags = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RegularBags")
PremiumBags = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PremiumBags")

# Add constraint to ensure the mix has at least CalciumMin units of calcium
model.addConstr(CalciumRegular * RegularBags + CalciumPremium * PremiumBags >= CalciumMin, name="calcium_min_requirement")

# Ensure that the mix has at least the minimum required units of vitamin mix
model.addConstr(VitaminMixRegular * RegularBags + VitaminMixPremium * PremiumBags >= VitaminMixMin, "VitaminMixRequirement")

# Add constraint to ensure the mix has at least ProteinMin units of protein
model.addConstr(ProteinRegular * RegularBags + ProteinPremium * PremiumBags >= ProteinMin, name="protein_requirement")

# Constraint to ensure the number of regular brand bags is non-negative
model.addConstr(RegularBags >= 0, name="nonnegativity_regular_bags")

# Constraint: The number of premium brand bags must be non-negative
model.addConstr(PremiumBags >= 0, name="premium_bags_non_negative")

# Ensure the minimum units of calcium are met constraint
model.addConstr(CalciumRegular * RegularBags + CalciumPremium * PremiumBags >= CalciumMin, name="calcium_requirement")

VitaminMixMin = data["VitaminMixMin"]  # scalar parameter
VitaminMixRegular = data["VitaminMixRegular"]  # scalar parameter
VitaminMixPremium = data["VitaminMixPremium"]  # scalar parameter

model.addConstr(VitaminMixRegular * RegularBags + VitaminMixPremium * PremiumBags >= VitaminMixMin, "min_vitamin_constraint")

# Ensure the minimum units of protein are met constraint
model.addConstr(ProteinRegular * RegularBags + ProteinPremium * PremiumBags >= ProteinMin, name="min_protein")

# Set objective
model.setObjective(CostRegular * RegularBags + CostPremium * PremiumBags, gp.GRB.MINIMIZE)

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
