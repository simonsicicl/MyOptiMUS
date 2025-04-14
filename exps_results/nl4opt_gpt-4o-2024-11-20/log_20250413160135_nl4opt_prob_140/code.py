import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_140/data.json", "r") as f:
    data = json.load(f)

DosePancreas1 = data["DosePancreas1"] # scalar parameter
DoseSkin1 = data["DoseSkin1"] # scalar parameter
DosePancreas2 = data["DosePancreas2"] # scalar parameter
DoseSkin2 = data["DoseSkin2"] # scalar parameter
DoseTumor1 = data["DoseTumor1"] # scalar parameter
DoseTumor2 = data["DoseTumor2"] # scalar parameter
MaxSkinDose = data["MaxSkinDose"] # scalar parameter
MinTumorDose = data["MinTumorDose"] # scalar parameter
MinutesBeam1 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MinutesBeam1")
MinutesBeam2 = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MinutesBeam2")

# Ensure that the minutes of Beam 1 used is non-negative
model.addConstr(MinutesBeam1 >= 0, name="non_negative_MinutesBeam1")

# Since the variable "MinutesBeam2" is already coded as a non-negative continuous variable, no additional code is needed.

# Adding the constraint for maximum allowable skin dose
model.addConstr(DoseSkin1 * MinutesBeam1 + DoseSkin2 * MinutesBeam2 <= MaxSkinDose, name="max_skin_dose_constraint")

# Add a constraint to ensure the tumor receives at least MinTumorDose units of medicine
model.addConstr(DoseTumor1 * MinutesBeam1 + DoseTumor2 * MinutesBeam2 >= MinTumorDose, name="tumor_min_dose")

# Ensure the tumor receives at least the minimum required dose
model.addConstr(
    DoseTumor1 * MinutesBeam1 + DoseTumor2 * MinutesBeam2 >= MinTumorDose, 
    name="min_tumor_dose"
)

# Add skin dose constraint
model.addConstr(
    DoseSkin1 * MinutesBeam1 + DoseSkin2 * MinutesBeam2 <= MaxSkinDose,
    name="skin_dose_constraint"
)

# Set objective
model.setObjective(DosePancreas1 * MinutesBeam1 + DosePancreas2 * MinutesBeam2, gp.GRB.MINIMIZE)

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
