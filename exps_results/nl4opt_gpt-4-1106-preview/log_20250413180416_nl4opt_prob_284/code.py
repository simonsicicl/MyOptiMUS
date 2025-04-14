import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_284/data.json", "r") as f:
    data = json.load(f)

A = data["A"] # scalar parameter
TimeHeavyDuty = data["TimeHeavyDuty"] # scalar parameter
TimeGasMower = data["TimeGasMower"] # scalar parameter
PollutionHeavyDuty = data["PollutionHeavyDuty"] # scalar parameter
FuelHeavyDuty = data["FuelHeavyDuty"] # scalar parameter
PollutionGasMower = data["PollutionGasMower"] # scalar parameter
FuelGasMower = data["FuelGasMower"] # scalar parameter
FuelTotal = data["FuelTotal"] # scalar parameter
PollutionMax = data["PollutionMax"] # scalar parameter
HeavyDutyCut = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HeavyDutyCut")
GasMowerCut = model.addVar(vtype=gp.GRB.CONTINUOUS, name="GasMowerCut")

HeavyDutyCut = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HeavyDutyCut")

# Constraint: Square feet cut by gas lawn mower is non-negative
model.addConstr(GasMowerCut >= 0, "nonnegativity_GasMowerCut")

# Add constraint for total square feet cut to equal the total area of grass land A
model.addConstr(HeavyDutyCut + GasMowerCut == A, name="total_cut_equals_A")

# Constraint: Total pollution from heavy-duty yard machine and gas lawn mower not exceeding the maximum allowable pollution
model.addConstr(PollutionHeavyDuty * HeavyDutyCut + PollutionGasMower * GasMowerCut <= PollutionMax, name="Max_Pollution")

# Add fuel consumption constraint
model.addConstr(FuelHeavyDuty * HeavyDutyCut + FuelGasMower * GasMowerCut <= FuelTotal, name="fuel_consumption")

# Constraint: Square footage cut by gas lawn mower must be non-negative
model.addConstr(GasMowerCut >= 0, name="nonnegativity_GasMowerCut")

# Add constraint for total square footage cut by both machines not exceeding the total area of grass land
model.addConstr(HeavyDutyCut + GasMowerCut <= A, name="area_cut_limit")

# Constraint: Sum of grass cut by heavy-duty and gas mower must be equal to the total area
model.addConstr(HeavyDutyCut + GasMowerCut == A, name="total_area_constraint")

# Total pollution generated by cutting machines must not exceed the maximum allowable pollution
model.addConstr(PollutionHeavyDuty * HeavyDutyCut + PollutionGasMower * GasMowerCut <= PollutionMax, name="pollution_limit")

# Fuel usage by cutting machines must not exceed the total amount of fuel available
model.addConstr(FuelHeavyDuty * HeavyDutyCut + FuelGasMower * GasMowerCut <= FuelTotal, "Fuel_Usage_Constraint")

# Set objective
model.setObjective(TimeHeavyDuty * HeavyDutyCut + TimeGasMower * GasMowerCut, gp.GRB.MINIMIZE)

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
