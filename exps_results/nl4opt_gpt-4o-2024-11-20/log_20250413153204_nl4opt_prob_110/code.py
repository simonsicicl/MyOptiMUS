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

# Add constraint to ensure ServingsSyrup1 is non-negative
model.addConstr(ServingsSyrup1 >= 0, name="non_negative_servings_syrup1")

# The non-negativity constraint is inherently satisfied as ServingsSyrup2 is defined as a continuous variable (vtype=gp.GRB.CONTINUOUS), which includes non-negative values by default.

# Add constraint to limit total medicine delivered to the throat
model.addConstr(
    ServingsSyrup1 * MedicineThroat1 + ServingsSyrup2 * MedicineThroat2 <= MaxMedicineThroat,
    name="throat_medicine_limit"
)

# Add constraint to ensure total medicine delivered to lungs meets or exceeds MinMedicineLungs
model.addConstr(ServingsSyrup1 * MedicineLungs1 + ServingsSyrup2 * MedicineLungs2 >= MinMedicineLungs, name="min_medicine_lungs")

# Add constraint for maximum medicine delivered to the throat
model.addConstr(
    ServingsSyrup1 * MedicineThroat1 + ServingsSyrup2 * MedicineThroat2 <= MaxMedicineThroat,
    name="max_medicine_throat_constraint"
)

# Add medicine delivery constraint to lungs
model.addConstr(
    MedicineLungs1 * ServingsSyrup1 + MedicineLungs2 * ServingsSyrup2 >= MinMedicineLungs,
    name="medicine_delivery_to_lungs"
)

# Set objective
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
