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

# Constraint for the total use of rare compound by both factories
model.addConstr(CompoundFactory1 * HoursFactory1 + CompoundFactory2 * HoursFactory2 <= TotalCompound, name="compound_usage")

# Add constraint to ensure at least the minimum required number of allergy pills are produced by both factories combined
model.addConstr(HoursFactory1 * AllergyPillsFactory1 + HoursFactory2 * AllergyPillsFactory2 >= MinAllergyPills, name="min_allergy_pills")

# Add constraint to ensure at least MinFeverPills fever reducing pills are produced
model.addConstr(FeverPillsFactory1 * HoursFactory1 + FeverPillsFactory2 * HoursFactory2 >= MinFeverPills, name="MinFeverPillsRequirement")

# Ensure factory operational hours are non-negative
model.addConstr(HoursFactory1 >= 0, name="NonNegativityHoursFactory1")
model.addConstr(HoursFactory2 >= 0, name="NonNegativityHoursFactory2")

# Ensure minimum required production of allergy pills is met
model.addConstr(HoursFactory1 * AllergyPillsFactory1 + HoursFactory2 * AllergyPillsFactory2 >= MinAllergyPills, name="min_allergy_pills_production")

# Ensure minimum required production of fever reducing pills is met
model.addConstr(HoursFactory1 * FeverPillsFactory1 + HoursFactory2 * FeverPillsFactory2 >= MinFeverPills, "min_fever_pills_production")

# Ensure the use of the rare compound does not exceed its availability
model.addConstr(HoursFactory1 * CompoundFactory1 + HoursFactory2 * CompoundFactory2 <= TotalCompound, "rare_compound_availability")

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
