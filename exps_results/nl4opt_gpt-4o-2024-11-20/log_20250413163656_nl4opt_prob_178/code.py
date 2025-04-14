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
NumberOfBikes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfBikes")
NumberOfCars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfCars")
PeopleTransportedByBikes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PeopleTransportedByBikes")
PeopleTransportedByCars = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PeopleTransportedByCars")
TotalVehicles = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalVehicles")

# The variable "NumberOfBikes" is non-negative due to its default lower bound (0) in Gurobi.

# No additional code needed since the variable "NumberOfCars" is non-negative by default (continuous variables in Gurobi are non-negative unless otherwise specified).

# Add constraint to ensure the number of people transported by bikes does not exceed bike capacity
model.addConstr(PeopleTransportedByBikes <= BikeCapacity * NumberOfBikes, name="people_bike_capacity")

# Adding constraint to ensure total people transported by cars does not exceed total seating capacity
model.addConstr(PeopleTransportedByCars <= NumberOfCars * CarCapacity, name="transport_capacity")

# Add constraint to ensure the number of cars is at most MaxCarProportion of total vehicles
model.addConstr(NumberOfCars <= MaxCarProportion * TotalVehicles, name="max_car_proportion")

model.addConstr(PeopleTransportedByBikes + PeopleTransportedByCars >= MinPeople, name="min_people_transport")

# Add transportation capacity constraint
model.addConstr(BikeCapacity * NumberOfBikes + CarCapacity * NumberOfCars >= MinPeople, name="transportation_capacity")

# Add constraint to ensure the number of cars is within the allowed maximum proportion
model.addConstr(NumberOfCars <= MaxCarProportion * (NumberOfBikes + NumberOfCars), name="max_car_proportion")

# Add constraint for minimum people transported
model.addConstr(PeopleTransportedByBikes + CarCapacity * NumberOfCars >= MinPeople, name="min_people_transport")

# Add transport demand constraint
model.addConstr(PeopleTransportedByCars + PeopleTransportedByBikes >= MinPeople, name="transport_demand_requirement")

# Add constraint ensuring the total number of vehicles equals the sum of bikes and cars
model.addConstr(TotalVehicles == NumberOfBikes + NumberOfCars, name="total_vehicles_constraint")

# Add constraint to ensure total people transported by bikes equals number of bikes times bike capacity
model.addConstr(PeopleTransportedByBikes == BikeCapacity * NumberOfBikes, name="bike_transportation_constraint")

# Add constraint to ensure the total number of people transported by cars matches the number of cars multiplied by the car capacity
model.addConstr(PeopleTransportedByCars == CarCapacity * NumberOfCars, name="people_transportation")

# Add constraint to ensure the total number of people transported by bikes and cars meets the minimum transportation requirement
model.addConstr(PeopleTransportedByBikes + PeopleTransportedByCars >= MinPeople, name="min_transportation_requirement")

# Add constraint ensuring people transported by bikes equals the number of bikes times bike capacity
model.addConstr(PeopleTransportedByBikes == NumberOfBikes * BikeCapacity, name="bike_transport_constraint")

# Add constraint to ensure the number of people transported by cars is equal to 
# the total number of cars multiplied by the seating capacity of a car
model.addConstr(PeopleTransportedByCars == NumberOfCars * CarCapacity, name="PeopleTransportedByCars_Constraint")

# Add constraint to ensure the proportion of cars does not exceed the maximum allowed proportion
model.addConstr(
    NumberOfCars <= MaxCarProportion * (NumberOfBikes + NumberOfCars), 
    name="max_car_proportion"
)

# Add constraint to define TotalVehicles as the sum of NumberOfBikes and NumberOfCars
model.addConstr(TotalVehicles == NumberOfBikes + NumberOfCars, name="total_vehicles_constraint")

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
