import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_93/data.json", "r") as f:
    data = json.load(f)

HydrogenA = data["HydrogenA"] # scalar parameter
PollutantsA = data["PollutantsA"] # scalar parameter
HydrogenB = data["HydrogenB"] # scalar parameter
PollutantsB = data["PollutantsB"] # scalar parameter
MinHydrogen = data["MinHydrogen"] # scalar parameter
MaxPollutants = data["MaxPollutants"] # scalar parameter
NumGeneratorA = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumGeneratorA")
NumGeneratorB = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumGeneratorB")

# The variable "NumGeneratorA" already has a non-negative domain by default in Gurobi as it is declared as CONTINUOUS.
# No additional constraint is needed for this requirement.

# No code is needed; the non-negativity constraint is automatically ensured due to the default non-negative domain of continuous variables in Gurobi.

# Add minimum hydrogen production constraint
model.addConstr(
    HydrogenA * NumGeneratorA + HydrogenB * NumGeneratorB >= MinHydrogen,
    name="min_hydrogen_production"
)

# Add constraint ensuring total pollutants from generators A and B do not exceed MaxPollutants
model.addConstr(NumGeneratorA * PollutantsA + NumGeneratorB * PollutantsB <= MaxPollutants, name="pollutants_limit")

# Add constraint to ensure total hydrogen produced meets the minimum requirement
model.addConstr((HydrogenA * NumGeneratorA) + (HydrogenB * NumGeneratorB) >= MinHydrogen, name="min_hydrogen_requirement")

# Add total pollutant constraint
model.addConstr((PollutantsA * NumGeneratorA) + (PollutantsB * NumGeneratorB) <= MaxPollutants, name="total_pollutants_constraint")

# Set objective
model.setObjective(NumGeneratorA + NumGeneratorB, gp.GRB.MINIMIZE)

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
