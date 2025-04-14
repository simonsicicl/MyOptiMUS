import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_18/data.json", "r") as f:
    data = json.load(f)

CostA = data["CostA"] # scalar parameter
CostB = data["CostB"] # scalar parameter
ProteinA = data["ProteinA"] # scalar parameter
ProteinB = data["ProteinB"] # scalar parameter
FatA = data["FatA"] # scalar parameter
FatB = data["FatB"] # scalar parameter
MinProtein = data["MinProtein"] # scalar parameter
MinFat = data["MinFat"] # scalar parameter
AmountA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AmountA")
AmountB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AmountB")

# Non-negativity constraint ensures that AmountA >= 0
model.addConstr(AmountA >= 0, name="non_negativity_AmountA")

# No code is needed as non-negativity is inherent to the default lower bound of Gurobi continuous variables,
# i.e., variables are >= 0 by default.

# Add protein constraint to ensure the mixture contains at least the required protein
model.addConstr(ProteinA * AmountA + ProteinB * AmountB >= MinProtein, name="protein_requirement")

# Add fat content constraint
model.addConstr(AmountA * FatA + AmountB * FatB >= MinFat, name="fat_content")

# Add protein constraint to ensure the mixture meets the minimum required units of protein
model.addConstr(ProteinA * AmountA + ProteinB * AmountB >= MinProtein, name="protein_constraint")

# Add the constraint to ensure the mixture meets the minimum required units of fat
model.addConstr(FatA * AmountA + FatB * AmountB >= MinFat, name="min_fat_requirement")

# Non-negativity constraint for the amount of Feed A
model.addConstr(AmountA >= 0, name="non_negativity_AmountA")

# Non-negativity constraint for the amount of Feed B
model.addConstr(AmountB >= 0, name="non_negativity_AmountB")

# Set objective
model.setObjective(CostA * AmountA + CostB * AmountB, gp.GRB.MINIMIZE)

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
