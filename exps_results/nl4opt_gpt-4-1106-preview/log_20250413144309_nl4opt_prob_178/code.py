import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_178/data.json", "r") as f:
    data = json.load(f)

BikeCapacity = data["BikeCapacity"] # scalar parameter
CarCapacity = data["CarCapacity"] # scalar parameter
MaxCarProportion = data["MaxCarProportion"] # scalar parameter
MinPeople = data["MinPeople"] # scalar parameter
NumberOfBikes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBikes")
NumberOfCars = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfCars")

# Add non-negativity constraint for the number of bikes used
model.addConstr(NumberOfBikes >= 0, name="non_negativity_bikes")

# The number of cars must be a non-negative value
model.addConstr(NumberOfCars >= 0, name="non_negative_cars")

model.addConstr(NumberOfBikes * BikeCapacity >= MinPeople, name="bike_capacity_constraint")

# Car capacity constraint to ensure enough transportation for minimum people accounting for bike capacity
model.addConstr(NumberOfCars * CarCapacity >= MinPeople - NumberOfBikes * BikeCapacity, name='car_capacity_constraint')

# Constraint: At most MaxCarProportion of the total number of vehicles can be cars
model.addConstr(NumberOfCars <= MaxCarProportion * (NumberOfBikes + NumberOfCars), name="MaxCarsProportionConstraint")

# At least MinPeople must be transported utilizing the available bikes and cars
model.addConstr(NumberOfBikes * BikeCapacity + NumberOfCars * CarCapacity >= MinPeople, "min_people_transportation")

# Ensure the minimum number of people are transported
model.addConstr(NumberOfBikes * BikeCapacity + NumberOfCars * CarCapacity >= MinPeople, name="min_people_transported")

# Add constraint to limit the number of cars based on the maximum car proportion
model.addConstr(NumberOfCars <= MaxCarProportion * (NumberOfBikes + NumberOfCars), "Car_Proportion_Limit")

# Set objective
model.setObjective(NumberOfBikes, gp.GRB.MINIMIZE)

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
