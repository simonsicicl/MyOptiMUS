import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_10/data.json", "r") as f:
    data = json.load(f)

NitrogenA = data["NitrogenA"] # scalar parameter
PhosphoricA = data["PhosphoricA"] # scalar parameter
VitaminAA = data["VitaminAA"] # scalar parameter
VitaminDA = data["VitaminDA"] # scalar parameter
NitrogenB = data["NitrogenB"] # scalar parameter
PhosphoricB = data["PhosphoricB"] # scalar parameter
VitaminAB = data["VitaminAB"] # scalar parameter
VitaminDB = data["VitaminDB"] # scalar parameter
MinNitrogen = data["MinNitrogen"] # scalar parameter
MinPhosphoric = data["MinPhosphoric"] # scalar parameter
MaxVitaminA = data["MaxVitaminA"] # scalar parameter
A = model.addVar(vtype=gp.GRB.CONTINUOUS, name="A")
B = model.addVar(vtype=gp.GRB.CONTINUOUS, name="B")

# Fertilizer A must be non-negative
model.addConstr(A >= 0, name="non_negativity_A")

# Fertilizer B is non-negative
model.addConstr(B >= 0, name="B_non_negative")

# Minimum nitrogen constraint
model.addConstr(NitrogenA * A + NitrogenB * B >= MinNitrogen, name="min_nitrogen")

# Add constraint for minimum required units of phosphoric acid
model.addConstr(PhosphoricA * A + PhosphoricB * B >= MinPhosphoric, name="min_phosphoric_acid")

# Constraint: Total units of vitamin A from both fertilizers should not exceed the maximum allowed
model.addConstr((VitaminAA * A) + (VitaminAB * B) <= MaxVitaminA, "max_vitamin_A")

# Set objective
model.setObjective(VitaminDA * A + VitaminDB * B, gp.GRB.MINIMIZE)

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
