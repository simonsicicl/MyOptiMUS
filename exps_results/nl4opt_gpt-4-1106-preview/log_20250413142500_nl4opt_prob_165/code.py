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
NumberOfBikes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBikes")
NumberOfScooters = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfScooters")
MealsPerBike = model.addVar(vtype=gp.GRB.INTEGER, name="MealsPerBike")
MealsPerScooter = model.addVar(vtype=gp.GRB.INTEGER, name="MealsPerScooter")

# Add constraint to ensure the number of bikes is non-negative
model.addConstr(NumberOfBikes >= 0, "numberOfBikes_nonneg")

# Since NumberOfScooters has already been defined as an integer variable, 
# we just need to add a constraint to ensure it is non-negative
model.addConstr(NumberOfScooters >= 0, name="non_negative_scooters")

# Add constraint to ensure non-negative and within capacity meals per bike
model.addConstr(MealsPerBike >= 0, name="min_meals")
model.addConstr(MealsPerBike <= BikeCapacity, name="max_capacity")

# Add scooter meal capacity constraints
model.addConstr(0 <= MealsPerScooter, name="min_meals_per_scooter")
model.addConstr(MealsPerScooter <= ScooterCapacity, name="max_meals_per_scooter")

# Add constraint for the total charge used by bikes and scooters not exceeding the total available charge
model.addConstr(NumberOfBikes * BikeCharge + NumberOfScooters * ScooterCharge <= TotalCharge, name="charge_capacity")

# At most MaxBikeRatio of the electric vehicles can be bikes
model.addConstr(NumberOfBikes <= MaxBikeRatio * (NumberOfBikes + NumberOfScooters), name="MaxBikeRatioConstraint")

# Add constraint for the minimum number of scooters
model.addConstr(NumberOfScooters >= MinScooters, name="min_scooters")

# Add constraint for bike's meal carrying capacity
model.addConstr(MealsPerBike <= BikeCapacity, name="MealsPerBike_capacity")

# Add constraint to ensure that the meals carried by the scooter do not exceed its capacity
model.addConstr(MealsPerScooter <= ScooterCapacity, name="scooter_capacity_constraint")

# Add constraint to ensure total charge used by all bikes and scooters does not exceed the total available charge
model.addConstr(NumberOfBikes * BikeCharge + NumberOfScooters * ScooterCharge <= TotalCharge, name="total_charge_limit")

# Proportion of bikes must not exceed the maximum bike ratio
model.addConstr(NumberOfBikes <= (NumberOfBikes + NumberOfScooters) * MaxBikeRatio, name="max_bike_ratio")

# Add constraint for minimum number of scooters
model.addConstr(NumberOfScooters >= MinScooters, name="min_scooters_constraint")

# Set objective
model.setObjective(NumberOfBikes * MealsPerBike + NumberOfScooters * MealsPerScooter, gp.GRB.MAXIMIZE)

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
