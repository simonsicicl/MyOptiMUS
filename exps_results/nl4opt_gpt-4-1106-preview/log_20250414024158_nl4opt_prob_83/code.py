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
NumberOfFourWheelers = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfFourWheelers")
NumberOfThreeWheelers = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfThreeWheelers")

# Constraint for non-negative number of 4-wheeler vehicles
model.addConstr(NumberOfFourWheelers >= 0, name="non_negative_four_wheelers")

# Since the variable NumberOfThreeWheelers is already defined as an integer variable, the non-negative constraint is implicitly satisfied.
# No code needed for enforcing the variable to be non-negative as it is the default nature of GRB.INTEGER type in Gurobi.

# Add constraint for minimum daily luggage capacity by vehicles
model.addConstr(NumberOfFourWheelers * CapacityFourWheeler + NumberOfThreeWheelers * CapacityThreeWheeler >= MinLuggageCapacity, name="min_luggage_capacity")

# Add pollution production constraint
model.addConstr(
    PollutionFourWheeler * NumberOfFourWheelers + 
    PollutionThreeWheeler * NumberOfThreeWheelers <= MaxPollution, 
    name="max_pollution"
)

# Add luggage movement capacity constraint to ensure it meets the minimum required per day
model.addConstr(
    CapacityFourWheeler * NumberOfFourWheelers + 
    CapacityThreeWheeler * NumberOfThreeWheelers >= 
    MinLuggageCapacity, 
    name="min_luggage_capacity"
)

# Add pollution constraint to ensure total pollution doesn't exceed maximum allowable per day
model.addConstr(
    PollutionFourWheeler * NumberOfFourWheelers + PollutionThreeWheeler * NumberOfThreeWheelers <= MaxPollution,
    name="max_daily_pollution"
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
