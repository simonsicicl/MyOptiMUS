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
TotalNumberOfLights = model.addVar(vtype=gp.GRB.INTEGER, name="TotalNumberOfLights")
NumberOfFluorescenceLamps = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfFluorescenceLamps")
NumberOfLedLights = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLedLights")

# Add constraint for minimum percentage of fluorescence lamps
model.addConstr(NumberOfFluorescenceLamps >= PFluorescence * TotalNumberOfLights, name="min_fluorescence_lamps")

# Ensure the total number of lights meets or exceeds the minimum required
model.addConstr(TotalNumberOfLights >= MinLights, name="min_lights_constraint")

# Total electricity usage constraint for LED fixtures and fluorescence lamps
model.addConstr(ELed * (TotalNumberOfLights - NumberOfFluorescenceLamps) + EFluorescence * NumberOfFluorescenceLamps <= MaxElectricity, name="ElectricityUsageLimit")

# Since NumberOfLedLights has already been added as an integer variable, we only need to set the constraint that it must be non-negative.
model.addConstr(NumberOfLedLights >= 0, name="LED_non_negative")

# Since NumberOfFluorescenceLamps is already declared as an integer variable, we just need to add the non-negativity constraint
model.addConstr(NumberOfFluorescenceLamps >= 0, name="fluorescence_lamps_nonnegativity")

# Add minimum light fixtures constraint
model.addConstr(TotalNumberOfLights >= MinLights, name="min_light_fixtures")

# Total number of lights installed should be the sum of LED lights and fluorescence lamps
model.addConstr(TotalNumberOfLights == NumberOfLedLights + NumberOfFluorescenceLamps, name="total_lights_constraint")

# Fluorescence lamps constraints:
model.addConstr(NumberOfFluorescenceLamps >= PFluorescence * TotalNumberOfLights, name="fluorescence_lamps_constraint")

# Add constraint to meet the minimum number of light fixtures required
model.addConstr(TotalNumberOfLights >= MinLights, name="min_lights_required")

# Constraint: Do not exceed maximum units of electricity that can be used
model.addConstr((NumberOfLedLights * ELed) + (NumberOfFluorescenceLamps * EFluorescence) <= MaxElectricity, "max_electricity_usage")

# Define the objective function
objective = NumberOfLedLights * NLed + NumberOfFluorescenceLamps * NFluorescence

# Set the objective to minimize the total number of light changes over a decade
model.setObjective(objective, gp.GRB.MINIMIZE)

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
