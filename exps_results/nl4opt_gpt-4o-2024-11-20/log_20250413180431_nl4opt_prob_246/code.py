import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_246/data.json", "r") as f:
    data = json.load(f)

ELed = data["ELed"] # scalar parameter
NLed = data["NLed"] # scalar parameter
EFluorescence = data["EFluorescence"] # scalar parameter
NFluorescence = data["NFluorescence"] # scalar parameter
PFluorescence = data["PFluorescence"] # scalar parameter
MinLights = data["MinLights"] # scalar parameter
MaxElectricity = data["MaxElectricity"] # scalar parameter
NumLEDLights = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumLEDLights")
NumFluorescenceLights = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumFluorescenceLights")

# Add constraint to ensure at least a proportion of installed fixtures are fluorescence lamps
model.addConstr(NumFluorescenceLights >= PFluorescence * (NumLEDLights + NumFluorescenceLights), name="min_fluorescence_lamps")

# Add constraint for total number of light fixtures
model.addConstr(NumLEDLights + NumFluorescenceLights >= MinLights, name="min_lights_constraint")

# Add electricity usage constraint
model.addConstr(
    NumLEDLights * ELed + NumFluorescenceLights * EFluorescence <= MaxElectricity, 
    name="electricity_usage_limit"
)

# No additional code needed since variable "NumLEDLights" is already non-negative due to its default lower bound (0) in Gurobi.

# The non-negativity of NumFluorescenceLights is inherently handled by its default domain in Gurobi,
# so no additional constraint code is required.

# Add constraint to ensure the total number of lights installed meets the minimum requirement (MinLights)
model.addConstr(NumLEDLights + NumFluorescenceLights >= MinLights, name="min_lights_requirement")

# Add constraint for the minimum number of lights required
model.addConstr(NumLEDLights + NumFluorescenceLights >= MinLights, name="min_lights_required")

# Add constraint to enforce minimum percentage of fluorescent lights
model.addConstr(NumFluorescenceLights >= PFluorescence * (NumLEDLights + NumFluorescenceLights), name="min_fluorescent_lights")

# Add maximum electricity usage constraint
model.addConstr(ELed * NumLEDLights + EFluorescence * NumFluorescenceLights <= MaxElectricity, name="MaxElectricityConstraint")

# Set objective
model.setObjective(NLed * NumLEDLights + NFluorescence * NumFluorescenceLights, gp.GRB.MINIMIZE)

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
