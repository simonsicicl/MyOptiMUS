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
ThroatSwabsNumber = model.addVar(vtype=gp.GRB.INTEGER, name="ThroatSwabsNumber")
NasalSwabsNumber = model.addVar(vtype=gp.GRB.INTEGER, name="NasalSwabsNumber")

# Since ThroatSwabTime is a non-negative scalar parameter and ThroatSwabsNumber is an integer variable,
# the product of a non-negative scalar and a variable will always be non-negative by definition of the variable type.
# Therefore, no explicit constraint needs to be added to the model.

# Since the time taken for one nasal swab is a positive constant, the product with the number of nasal swabs will be non-negative by definition.
# Therefore, no additional constraint is needed to guarantee non-negativity.

# Add constraint to ensure the minimum number of nasal swabs is administered
model.addConstr(NasalSwabsNumber >= MinNasalSwabs, name="min_nasal_swabs")

# Add constraint for minimum throat to nasal swabs ratio
model.addConstr(ThroatSwabsNumber >= ThroatNasalRatio * NasalSwabsNumber, name="throat_to_nasal_ratio")

# Add constraint for the total time for administering both types of swabs not exceeding the available total time
model.addConstr(ThroatSwabTime * ThroatSwabsNumber + NasalSwabTime * NasalSwabsNumber <= TotalTime, name="total_swab_time")

# Total operational time constraint for throat and nasal swabs
model.addConstr(ThroatSwabTime * ThroatSwabsNumber + NasalSwabTime * NasalSwabsNumber <= TotalTime, name="total_operational_time")

# Add a constraint to ensure the minimum number of nasal swabs is met
model.addConstr(NasalSwabsNumber >= MinNasalSwabs, name="min_nasal_swabs")

# Add constraint for the minimum ratio of throat to nasal swabs
model.addConstr(ThroatSwabsNumber >= ThroatNasalRatio * NasalSwabsNumber, name="min_ratio_throat_to_nasal_swabs")

# Set objective
model.setObjective(ThroatSwabsNumber + NasalSwabsNumber, gp.GRB.MAXIMIZE)

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
