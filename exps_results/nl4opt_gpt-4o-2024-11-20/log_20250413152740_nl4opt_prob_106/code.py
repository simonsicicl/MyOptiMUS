import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_106/data.json", "r") as f:
    data = json.load(f)

AllergyPillsFactory1 = data["AllergyPillsFactory1"] # scalar parameter
FeverPillsFactory1 = data["FeverPillsFactory1"] # scalar parameter
AllergyPillsFactory2 = data["AllergyPillsFactory2"] # scalar parameter
FeverPillsFactory2 = data["FeverPillsFactory2"] # scalar parameter
CompoundFactory1 = data["CompoundFactory1"] # scalar parameter
CompoundFactory2 = data["CompoundFactory2"] # scalar parameter
TotalCompound = data["TotalCompound"] # scalar parameter
MinAllergyPills = data["MinAllergyPills"] # scalar parameter
MinFeverPills = data["MinFeverPills"] # scalar parameter
HoursFactory1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursFactory1")
HoursFactory2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HoursFactory2")

# Adding a constraint to ensure total usage of the rare compound across both factories does not exceed available capacity.
model.addConstr(
    HoursFactory1 * CompoundFactory1 + HoursFactory2 * CompoundFactory2 <= TotalCompound,
    name="rare_compound_usage"
)

# Add constraint to ensure total allergy pills produced is at least MinAllergyPills
model.addConstr(AllergyPillsFactory1 * HoursFactory1 + AllergyPillsFactory2 * HoursFactory2 >= MinAllergyPills, name="min_allergy_pills")

# Ensure that at least MinFeverPills fever reducing pills are produced
model.addConstr(
    (HoursFactory1 * FeverPillsFactory1) + (HoursFactory2 * FeverPillsFactory2) >= MinFeverPills,
    name="MinFeverPillsConstraint"
)

# The non-negativity constraint for factory operational hours is enforced inherently by setting the lower bound to 0 when defining the variables (vtype=gp.GRB.CONTINUOUS).  
# Hence, no additional code is needed.

# Non-negativity constraint for HoursFactory1
model.addConstr(HoursFactory1 >= 0, name="non_negativity_hoursfactory1")

# Non-negativity constraint for HoursFactory2
model.addConstr(HoursFactory2 >= 0, name="non_negativity_hours_factory2")

# Add minimum production requirement constraint for allergy pills
model.addConstr(AllergyPillsFactory1 * HoursFactory1 + AllergyPillsFactory2 * HoursFactory2 >= MinAllergyPills, name="min_allergy_pills")

# Add minimum production constraints for fever-reducing pills
model.addConstr(
    FeverPillsFactory1 * HoursFactory1 + FeverPillsFactory2 * HoursFactory2 >= MinFeverPills, 
    name="min_fever_pills_production"
)

# Add constraint for limited availability of the rare compound across both factories
model.addConstr(
    CompoundFactory1 * HoursFactory1 + CompoundFactory2 * HoursFactory2 <= TotalCompound,
    name="rare_compound_limit"
)

# Set objective
model.setObjective(HoursFactory1 + HoursFactory2, gp.GRB.MINIMIZE)

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
