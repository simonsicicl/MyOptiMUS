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
AmountFertilizerA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AmountFertilizerA")
AmountFertilizerB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AmountFertilizerB")

# Add constraint to ensure the amount of fertilizer A is non-negative
model.addConstr(AmountFertilizerA >= 0, name="fertilizer_A_non_negative")

# No code is needed because non-negativity is already ensured by default in gurobipy for continuous variables.

# Add nitrogen constraint ensuring enough nitrogen from fertilizers A and B
model.addConstr(NitrogenA * AmountFertilizerA + NitrogenB * AmountFertilizerB >= MinNitrogen, name="nitrogen_requirement")

# Add constraint to ensure the total amount of phosphoric acid meets the minimum requirement
model.addConstr(PhosphoricA * AmountFertilizerA + PhosphoricB * AmountFertilizerB >= MinPhosphoric, name="min_phosphoric_constraint")

# Add constraint for maximum Vitamin A  
model.addConstr(VitaminAA * AmountFertilizerA + VitaminAB * AmountFertilizerB <= MaxVitaminA, name="MaxVitaminA_constraint")

# Add minimum nitrogen requirement constraint
model.addConstr(NitrogenA * AmountFertilizerA + NitrogenB * AmountFertilizerB >= MinNitrogen, 
                name="min_nitrogen_requirement")

# Add minimum phosphoric acid requirement constraint
model.addConstr(
    PhosphoricA * AmountFertilizerA + PhosphoricB * AmountFertilizerB >= MinPhosphoric,
    name="min_phosphoric_requirement"
)

# Add maximum allowed vitamin A constraint
model.addConstr(
    VitaminAA * AmountFertilizerA + VitaminAB * AmountFertilizerB <= MaxVitaminA,
    name="max_vitamin_a_constraint"
)

# Set objective
model.setObjective(VitaminDA * AmountFertilizerA + VitaminDB * AmountFertilizerB, gp.GRB.MINIMIZE)

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
