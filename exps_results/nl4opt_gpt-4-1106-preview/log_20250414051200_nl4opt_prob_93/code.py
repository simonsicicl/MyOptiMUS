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
NumberOfGeneratorA = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfGeneratorA")
NumberOfGeneratorB = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfGeneratorB")

# The variable NumberOfGeneratorA is non-negative by default since it is an integer variable in Gurobi.
# No additional code is needed for this constraint.

# Ensure that the number of generator B units is non-negative
model.addConstr(NumberOfGeneratorB >= 0, name="genB_non_negative")

# Total hydrogen production must meet or exceed the minimum required production constraint
MinHydrogen = data["MinHydrogen"] # scalar parameter
model.addConstr(HydrogenA * NumberOfGeneratorA + HydrogenB * NumberOfGeneratorB >= MinHydrogen, name="min_hydrogen_production")

# Ensure total pollutants do not exceed maximum allowed
model.addConstr(NumberOfGeneratorA * PollutantsA + NumberOfGeneratorB * PollutantsB <= MaxPollutants, name="max_pollutants")

# Ensure the minimum hydrogen production requirement is met
model.addConstr(NumberOfGeneratorA * HydrogenA + NumberOfGeneratorB * HydrogenB >= MinHydrogen, "hydrogen_production_requirement")

# Ensure the pollutant production does not exceed the maximum allowed
model.addConstr(NumberOfGeneratorA * PollutantsA + NumberOfGeneratorB * PollutantsB <= MaxPollutants, "PollutantProductionConstraint")

# Set objective
model.setObjective(NumberOfGeneratorA + NumberOfGeneratorB, gp.GRB.MINIMIZE)

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
