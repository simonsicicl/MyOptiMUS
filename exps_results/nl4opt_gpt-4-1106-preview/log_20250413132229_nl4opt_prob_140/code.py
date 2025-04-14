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

# Constraint: Minutes of Beam 1 used is non-negative
model.addConstr(MinutesBeam1 >= 0, name="nonnegativity_MinutesBeam1")

model.addConstr(MinutesBeam2 >= 0, name="non_negativity_beam2")

# Add constraint for maximum skin dose from both beams
model.addConstr(DoseSkin1 * MinutesBeam1 + DoseSkin2 * MinutesBeam2 <= MaxSkinDose, name="max_skin_dose_constraint")

# Add constraint for minimum tumor dose
model.addConstr(MinutesBeam1 * DoseTumor1 + MinutesBeam2 * DoseTumor2 >= MinTumorDose, name="min_tumor_dose")

# Add constraint for the maximum allowed dose to the skin
model.addConstr(DoseSkin1 * MinutesBeam1 + DoseSkin2 * MinutesBeam2 <= MaxSkinDose, name="max_skin_dose")

# Ensure the tumor receives at least the minimum required dose
model.addConstr(DoseTumor1 * MinutesBeam1 + DoseTumor2 * MinutesBeam2 >= MinTumorDose, name="min_tumor_dose")

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
