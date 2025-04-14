import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_129/data.json", "r") as f:
    data = json.load(f)

ThroatSwabTime = data["ThroatSwabTime"] # scalar parameter
NasalSwabTime = data["NasalSwabTime"] # scalar parameter
MinNasalSwabs = data["MinNasalSwabs"] # scalar parameter
ThroatNasalRatio = data["ThroatNasalRatio"] # scalar parameter
TotalTime = data["TotalTime"] # scalar parameter
NumberOfThroatSwabs = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfThroatSwabs")
NumberOfNasalSwabs = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfNasalSwabs")

# Add non-negativity constraints
model.addConstr(NumberOfThroatSwabs >= 0, name="non_negativity_throat")
model.addConstr(NumberOfNasalSwabs >= 0, name="non_negativity_nasal")

# Add time constraint
model.addConstr(ThroatSwabTime * NumberOfThroatSwabs + NasalSwabTime * NumberOfNasalSwabs <= TotalTime, name="time_constraint")

# Add minimum nasal swabs constraint
model.addConstr(NumberOfNasalSwabs >= MinNasalSwabs, name="minimum_nasal_swabs")

# Add throat-to-nasal swab ratio constraint
model.addConstr(NumberOfThroatSwabs >= ThroatNasalRatio * NumberOfNasalSwabs, name="throat_nasal_ratio")

# Constraint is inherent to the variable definition: no separate code needed as variable's domain already ensures non-negativity (GRB.CONTINUOUS defaults to non-negativity)

# Add constraint to ensure at least MinNasalSwabs nasal swabs are performed
model.addConstr(NumberOfNasalSwabs >= MinNasalSwabs, name="min_nasal_swabs_constraint")

# Add constraint to ensure throat swabs are at least ThroatNasalRatio times nasal swabs
model.addConstr(NumberOfThroatSwabs >= ThroatNasalRatio * NumberOfNasalSwabs, name="throat_nasal_ratio")

# Add total time constraint
model.addConstr(
    ThroatSwabTime * NumberOfThroatSwabs + NasalSwabTime * NumberOfNasalSwabs <= TotalTime,
    name="total_time_constraint"
)

# Add constraint to ensure the number of nasal swabs meets the minimum requirement
model.addConstr(NumberOfNasalSwabs >= MinNasalSwabs, name="minimum_nasal_swabs")

# Add throat-to-nasal swab ratio constraint
model.addConstr(NumberOfThroatSwabs >= ThroatNasalRatio * NumberOfNasalSwabs, name="throat_nasal_ratio")

# Add constraint ensuring total swabbing time does not exceed allocated operational time
model.addConstr(
    (ThroatSwabTime * NumberOfThroatSwabs) + (NasalSwabTime * NumberOfNasalSwabs) <= TotalTime,
    name="operational_time_constraint"
)

# Add constraint on total time spent on swabs
model.addConstr(
    ThroatSwabTime * NumberOfThroatSwabs + NasalSwabTime * NumberOfNasalSwabs <= TotalTime,
    name="TotalTimeConstraint"
)

# Add constraint ensuring the number of nasal swabs meets the minimum required
model.addConstr(NumberOfNasalSwabs >= MinNasalSwabs, name="minimum_nasal_swabs")

# Add throat-to-nasal ratio constraint
model.addConstr(NumberOfThroatSwabs >= ThroatNasalRatio * NumberOfNasalSwabs, name="throat_nasal_ratio")

# Set objective
model.setObjective(NumberOfThroatSwabs + NumberOfNasalSwabs, gp.GRB.MAXIMIZE)

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
