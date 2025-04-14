import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_165/data.json", "r") as f:
    data = json.load(f)

BikeCapacity = data["BikeCapacity"] # scalar parameter
BikeCharge = data["BikeCharge"] # scalar parameter
ScooterCapacity = data["ScooterCapacity"] # scalar parameter
ScooterCharge = data["ScooterCharge"] # scalar parameter
MaxBikeRatio = data["MaxBikeRatio"] # scalar parameter
MinScooters = data["MinScooters"] # scalar parameter
TotalCharge = data["TotalCharge"] # scalar parameter
NumberOfBikes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBikes")
NumberOfScooters = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfScooters")
MealsPerBike = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MealsPerBike")
MealsPerScooter = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MealsPerScooter")

# The variable "NumberOfBikes" is already defined as non-negative (continuous), no additional constraint is needed.

# No additional code is needed because the non-negativity is inherent due to the default non-negative domain of continuous variables in Gurobi.

# Add constraint ensuring the number of meals per bike is non-negative and does not exceed the bike's capacity
model.addConstr(MealsPerBike >= 0, name="non_negative_meals")
model.addConstr(MealsPerBike <= BikeCapacity, name="meals_within_capacity")

# Add constraints to ensure MealsPerScooter is non-negative and does not exceed ScooterCapacity
model.addConstr(MealsPerScooter >= 0, name="MealsPerScooter_non_negative")
model.addConstr(MealsPerScooter <= ScooterCapacity, name="MealsPerScooter_capacity_limit")

# Add total charge usage constraint
model.addConstr(BikeCharge * NumberOfBikes + ScooterCharge * NumberOfScooters <= TotalCharge, name="total_charge_constraint")

model.addConstr((1 - MaxBikeRatio) * NumberOfBikes <= MaxBikeRatio * NumberOfScooters, name="bike_ratio_constraint")

# Add constraint to ensure at least MinScooters scooters are used
model.addConstr(NumberOfScooters >= MinScooters, name="min_scooters_constraint")

# Add constraint to ensure total charge for bikes and scooters does not exceed available charge
model.addConstr((NumberOfBikes * BikeCharge) + (NumberOfScooters * ScooterCharge) <= TotalCharge, name="charge_limit")

# Add proportion constraint for bikes
model.addConstr(NumberOfBikes <= MaxBikeRatio * (NumberOfBikes + NumberOfScooters), name="bike_ratio_constraint")

# Add constraint ensuring the number of scooters is at least the minimum required
model.addConstr(NumberOfScooters >= MinScooters, name="min_scooters_constraint")

# Set objective  
model.setObjective((NumberOfBikes * MealsPerBike) + (NumberOfScooters * MealsPerScooter), gp.GRB.MAXIMIZE)

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
