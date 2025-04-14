import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_110/data.json", "r") as f:
    data = json.load(f)

MedicineThroat1 = data["MedicineThroat1"] # scalar parameter
MedicineLungs1 = data["MedicineLungs1"] # scalar parameter
MedicineThroat2 = data["MedicineThroat2"] # scalar parameter
MedicineLungs2 = data["MedicineLungs2"] # scalar parameter
Sugar1 = data["Sugar1"] # scalar parameter
Sugar2 = data["Sugar2"] # scalar parameter
MaxMedicineThroat = data["MaxMedicineThroat"] # scalar parameter
MinMedicineLungs = data["MinMedicineLungs"] # scalar parameter
ServingsSyrup1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsSyrup1")
ServingsSyrup2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ServingsSyrup2")

model.addConstr(ServingsSyrup1 >= 0, name="non_negative_servings_syrup1")

model.addConstr(ServingsSyrup2 >= 0, name="non_negative_servings_syrup2")

model.addConstr(MedicineThroat1 * ServingsSyrup1 + MedicineThroat2 * ServingsSyrup2 <= MaxMedicineThroat, name="MaxMedicineThroatConstraint")

# Add constraint for minimum medicine delivered to the lungs
model.addConstr(MedicineLungs1 * ServingsSyrup1 + MedicineLungs2 * ServingsSyrup2 >= MinMedicineLungs, name="min_medicine_to_lungs")

# Add constraint for the maximum medicine delivered to the throat by the syrups
model.addConstr(MedicineThroat1 * ServingsSyrup1 + MedicineThroat2 * ServingsSyrup2 <= MaxMedicineThroat, name="max_medicine_throat")

# Constraint to ensure the total medicine delivered to the lungs by the syrups meets or exceeds the minimum requirement
model.addConstr(MedicineLungs1 * ServingsSyrup1 + MedicineLungs2 * ServingsSyrup2 >= MinMedicineLungs, "min_medicine_to_lungs")

# Objective function: Minimize the patient's total sugar intake from consuming syrups
model.setObjective(Sugar1 * ServingsSyrup1 + Sugar2 * ServingsSyrup2, gp.GRB.MINIMIZE)

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
