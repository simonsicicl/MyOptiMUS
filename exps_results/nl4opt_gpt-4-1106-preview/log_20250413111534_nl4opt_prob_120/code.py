import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_120/data.json", "r") as f:
    data = json.load(f)

MedicineHeartMachine1 = data["MedicineHeartMachine1"] # scalar parameter
MedicineHeartMachine2 = data["MedicineHeartMachine2"] # scalar parameter
MedicineBrainMachine1 = data["MedicineBrainMachine1"] # scalar parameter
MedicineBrainMachine2 = data["MedicineBrainMachine2"] # scalar parameter
WasteMachine1 = data["WasteMachine1"] # scalar parameter
WasteMachine2 = data["WasteMachine2"] # scalar parameter
MaxMedicineHeart = data["MaxMedicineHeart"] # scalar parameter
MinMedicineBrain = data["MinMedicineBrain"] # scalar parameter
MinutesOnMachine1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MinutesOnMachine1")
MinutesOnMachine2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MinutesOnMachine2")

# Since MinutesOnMachine1 is already a non-negative continuous variable by virtue of its definition, no additional constraint is needed.
# The Gurobi default lower bound for continuous variables is 0, which enforces the non-negativity.

# Constraint: Minutes on machine 2 must be non-negative
model.addConstr(MinutesOnMachine2 >= 0, name="non_negative_machine2")

# Add constraint for maximum medicine delivered to the heart
model.addConstr(MedicineHeartMachine1 * MinutesOnMachine1 + MedicineHeartMachine2 * MinutesOnMachine2 <= MaxMedicineHeart, "max_medicine_heart_constraint")

# Add constraint to ensure the brain receives at least the minimum required units of medicine
model.addConstr(MedicineBrainMachine1 * MinutesOnMachine1 + MedicineBrainMachine2 * MinutesOnMachine2 >= MinMedicineBrain, "MinMedicineBrainConstraint")

# Ensure the heart receives at most a maximum units of medicine
heart_medicine_constraint = MedicineHeartMachine1 * MinutesOnMachine1 + MedicineHeartMachine2 * MinutesOnMachine2 <= MaxMedicineHeart
model.addConstr(heart_medicine_constraint, name="max_heart_medicine_constraint")

# Ensure the brain receives at least a minimum units of medicine
model.addConstr(MedicineBrainMachine1 * MinutesOnMachine1 + MedicineBrainMachine2 * MinutesOnMachine2 >= MinMedicineBrain, name="min_medicine_to_brain")

# Set objective
model.setObjective(WasteMachine1 * MinutesOnMachine1 + WasteMachine2 * MinutesOnMachine2, gp.GRB.MINIMIZE)

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
