import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_186/data.json", "r") as f:
    data = json.load(f)

CapacityCow = data["CapacityCow"] # scalar parameter
CapacityElephant = data["CapacityElephant"] # scalar parameter
MinBricks = data["MinBricks"] # scalar parameter
MaxCowElephantRatio = data["MaxCowElephantRatio"] # scalar parameter
MaxElephantsToCows = data["MaxElephantsToCows"] # scalar parameter
NumberElephants = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberElephants")
NumberCows = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberCows")

# Add constraint ensuring the number of elephants does not exceed the number of cows
model.addConstr(NumberElephants <= NumberCows, name="elephants_cannot_exceed_cows")

# Add constraint ensuring the number of cows does not exceed MaxCowElephantRatio times the number of elephants
model.addConstr(NumberCows <= MaxCowElephantRatio * NumberElephants, name="CowElephantRatio")

# Add constraint ensuring the total bricks transported meet or exceed the minimum required
model.addConstr(
    NumberElephants * CapacityElephant + NumberCows * CapacityCow >= MinBricks,
    name="min_bricks_transport"
)

# As the non-negativity constraint is already satisfied due to the variable being defined as continuous with no lower bound change needed, no additional code is required.

# The non-negativity of the continuous variable NumberElephants is already enforced by default in Gurobi

# Add total capacity constraint for cows and elephants
model.addConstr(
    CapacityCow * NumberCows + CapacityElephant * NumberElephants >= MinBricks,
    name="total_capacity_constraint"
)

# Add constraint to ensure the number of cows does not exceed the maximum allowed ratio of cows to elephants
model.addConstr(NumberCows <= MaxCowElephantRatio * NumberElephants, name="cow_to_elephant_ratio")

# Add constraint ensuring the number of elephants does not exceed the maximum allowed ratio to cows
model.addConstr(NumberElephants <= MaxElephantsToCows * NumberCows, name="ElephantToCowRatio")

# Set objective
model.setObjective(NumberCows + NumberElephants, gp.GRB.MINIMIZE)

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
