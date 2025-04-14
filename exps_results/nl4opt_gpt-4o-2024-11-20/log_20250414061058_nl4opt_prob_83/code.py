import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_83/data.json", "r") as f:
    data = json.load(f)

CapacityFourWheeler = data["CapacityFourWheeler"] # scalar parameter
PollutionFourWheeler = data["PollutionFourWheeler"] # scalar parameter
CapacityThreeWheeler = data["CapacityThreeWheeler"] # scalar parameter
PollutionThreeWheeler = data["PollutionThreeWheeler"] # scalar parameter
MinLuggageCapacity = data["MinLuggageCapacity"] # scalar parameter
MaxPollution = data["MaxPollution"] # scalar parameter
NumberOfFourWheelers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfFourWheelers")
NumberOfThreeWheelers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfThreeWheelers")

# Add non-negativity constraint for the number of 4-wheeler vehicles
model.addConstr(NumberOfFourWheelers >= 0, name="non_negativity_4wheelers")

# Non-negativity constraint is inherently handled in gurobipy since the default lower bound for continuous variables is 0.
# No additional code is needed for this constraint.

# Add luggage capacity constraint
model.addConstr(
    NumberOfFourWheelers * CapacityFourWheeler + NumberOfThreeWheelers * CapacityThreeWheeler >= MinLuggageCapacity,
    name="luggage_capacity_constraint"
)

# Add pollution limit constraint
model.addConstr(PollutionFourWheeler * NumberOfFourWheelers + PollutionThreeWheeler * NumberOfThreeWheelers <= MaxPollution, name="pollution_limit")

# Ensure the total luggage movement capacity meets or exceeds the minimum requirement
model.addConstr(NumberOfFourWheelers * CapacityFourWheeler + NumberOfThreeWheelers * CapacityThreeWheeler >= MinLuggageCapacity, 
                name="min_luggage_capacity_constraint")

# Ensure the total pollution output does not exceed the maximum allowable pollution
model.addConstr(
    NumberOfFourWheelers * PollutionFourWheeler + NumberOfThreeWheelers * PollutionThreeWheeler <= MaxPollution,
    name="max_pollution_constraint"
)

# Set objective
model.setObjective(NumberOfFourWheelers + NumberOfThreeWheelers, gp.GRB.MINIMIZE)

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
