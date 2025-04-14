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
FeedA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FeedA")
FeedB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FeedB")

# Add non-negativity constraint for the amount of Feed A
model.addConstr(FeedA >= 0, name="feedA_non_negativity")

model.addConstr(FeedB >= 0, name="FeedB_non_negative")

# Add constraint to ensure mixture contains at least MinProtein units of protein
model.addConstr(ProteinA * FeedA + ProteinB * FeedB >= MinProtein, name="min_protein")

# The mixture must contain at least MinFat units of fat
model.addConstr(FatA * FeedA + FatB * FeedB >= MinFat, name="min_fat_requirement")

# Add minimum protein constraint
model.addConstr(ProteinA * FeedA + ProteinB * FeedB >= MinProtein, name="min_protein")

# Add constraint: the mixture should meet the minimum required units of fat
model.addConstr(FatA * FeedA + FatB * FeedB >= MinFat, name="min_fat_requirement")

# Define the objective function
model.setObjective(CostA * FeedA + CostB * FeedB, gp.GRB.MINIMIZE)

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
