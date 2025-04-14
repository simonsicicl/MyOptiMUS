import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_177/data.json", "r") as f:
    data = json.load(f)

Tc = data["Tc"] # scalar parameter
Cc = data["Cc"] # scalar parameter
Ratio = data["Ratio"] # scalar parameter
MinCorn = data["MinCorn"] # scalar parameter
CornInTractor = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CornInTractor")
NumCars = model.addVar(vtype=gp.GRB.INTEGER, name="NumCars")
CornInCar = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CornInCar")
NumTractors = model.addVar(vtype=gp.GRB.INTEGER, name="NumTractors")

# Add constraint for the capacity of the tractor for carrying corn
model.addConstr(CornInTractor <= Tc, name="tractor_corn_capacity")

# Add constraint for the maximum amount of corn that can be carried by all cars
model.addConstr(CornInCar <= NumCars * Cc, name="car_corn_capacity")

# At least Ratio times tractors constraint
model.addConstr(NumCars >= Ratio * (CornInTractor / Tc), name="car_to_tractor_ratio_constraint")

# Add constraint to ensure the total amount of corn sent to the city is at least the minimum required amount
model.addConstr(CornInTractor + CornInCar >= MinCorn, name="min_corn_requirement")

# Add constraint to ensure the number of tractors is non-negative
model.addConstr(NumTractors >= 0, name="NonNegTractors")

# Add constraint to ensure the number of cars is non-negative
model.addConstr(NumCars >= 0, name="num_cars_non_negative")

# Ensure that the total weight of corn sent by tractors and cars meets the minimum requirement
model.addConstr((NumTractors * Tc) + (NumCars * Cc) >= MinCorn, name="meet_min_corn_requirement")

# Ensure that the ratio of the number of cars to the number of tractors is at least the minimum ratio
model.addConstr(NumCars >= Ratio * NumTractors, name="min_cars_tractors_ratio")

# Set objective
model.setObjective(NumTractors + NumCars, gp.GRB.MINIMIZE)

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
