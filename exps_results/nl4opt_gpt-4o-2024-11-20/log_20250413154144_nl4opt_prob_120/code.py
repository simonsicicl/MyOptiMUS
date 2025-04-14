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
MinutesMachine1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MinutesMachine1")
MinutesMachine2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MinutesMachine2")

# The operational time for machine 1 is constrained to be non-negative
model.addConstr(MinutesMachine1 >= 0, name="non_negative_minutes_machine1")

# The operational time on Machine 2 must be non-negative
model.addConstr(MinutesMachine2 >= 0, name="non_negative_operational_time")

# Add constraint: The amount of medicine delivered to the heart by both machines combined should not exceed the maximum allowed units
model.addConstr(
    MedicineHeartMachine1 * MinutesMachine1 + MedicineHeartMachine2 * MinutesMachine2 <= MaxMedicineHeart,
    name="medicine_heart_constraint"
)

# Add constraint to ensure the brain receives at least MinMedicineBrain units of medicine
model.addConstr(
    MinutesMachine1 * MedicineBrainMachine1 + MinutesMachine2 * MedicineBrainMachine2 >= MinMedicineBrain,
    name="brain_medicine_minimum"
)

# Add constraint: Medicine delivered to the heart should not exceed its maximum capacity  
model.addConstr(  
    MinutesMachine1 * MedicineHeartMachine1 + MinutesMachine2 * MedicineHeartMachine2 <= MaxMedicineHeart,  
    name="medicine_heart_capacity"  
)

# Add constraint to ensure minimum medicine delivery to the brain
model.addConstr(
    MinutesMachine1 * MedicineBrainMachine1 + MinutesMachine2 * MedicineBrainMachine2 >= MinMedicineBrain,
    name="min_medicine_brain"
)

# Add non-negativity constraints for operational times
model.addConstr(MinutesMachine1 >= 0, name="non_negativity_Machine1")
model.addConstr(MinutesMachine2 >= 0, name="non_negativity_Machine2")

# Set objective
model.setObjective(MinutesMachine1 * WasteMachine1 + MinutesMachine2 * WasteMachine2, gp.GRB.MINIMIZE)

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
