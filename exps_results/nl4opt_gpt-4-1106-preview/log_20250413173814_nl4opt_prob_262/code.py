import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_262/data.json", "r") as f:
    data = json.load(f)

MinLocals = data["MinLocals"] # scalar parameter
PeoplePerKayak = data["PeoplePerKayak"] # scalar parameter
PeoplePerMotorboat = data["PeoplePerMotorboat"] # scalar parameter
TimePerKayak = data["TimePerKayak"] # scalar parameter
TimePerMotorboat = data["TimePerMotorboat"] # scalar parameter
MaxMotorboatTrips = data["MaxMotorboatTrips"] # scalar parameter
MinPercentKayakTrips = data["MinPercentKayakTrips"] # scalar parameter
NumKayakTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumKayakTrips")
NumMotorboatTrips = model.addVar(vtype=gp.GRB.INTEGER, name="NumMotorboatTrips")
TotalPeopleKayak = model.addVar(vtype=gp.GRB.INTEGER, name="TotalPeopleKayak")
TotalPeopleMotorboat = model.addVar(vtype=gp.GRB.INTEGER, name="TotalPeopleMotorboat")

# Transport a minimum number of locals across the lake
model.addConstr(PeoplePerKayak * NumKayakTrips + PeoplePerMotorboat * NumMotorboatTrips >= MinLocals, name="min_locals_constraint")

# Constraint: Total number of people transported via kayak cannot exceed the number of kayak trips times the number of people per kayak
model.addConstr(NumKayakTrips * PeoplePerKayak >= TotalPeopleKayak, name="kayak_people_constraint")

# Add constraint to limit the total number of people transported by motorboat to the product of the number of motorboat trips and the number of people per motorboat trip
model.addConstr(TotalPeopleMotorboat <= NumMotorboatTrips * PeoplePerMotorboat, name="motorboat_people_limit")

# Add constraint on the maximum number of motorboat trips
model.addConstr(NumMotorboatTrips <= MaxMotorboatTrips, name="max_motorboat_trips")

# At least MinPercentKayakTrips% of the total trips must be by kayak
model.addConstr(NumKayakTrips >= MinPercentKayakTrips * (NumKayakTrips + NumMotorboatTrips), name="min_kayak_trips")

# Ensure that the percentage of kayak trips is at least the minimum required
model.addConstr((1 - MinPercentKayakTrips) * NumKayakTrips >= MinPercentKayakTrips * NumMotorboatTrips, name="min_kayak_trips_percentage")



# Ensure that the number of trips by motorboat does not exceed the maximum allowed
model.addConstr(NumMotorboatTrips <= MaxMotorboatTrips, name="num_motorboat_trips_constraint")

# Ensure that at least the minimum percentage of the trips are made by kayaks
model.addConstr((NumKayakTrips >= MinPercentKayakTrips * (NumKayakTrips + NumMotorboatTrips)), name="min_kayak_trips_percent")

# Relate the total number of people transported by kayak to the number of kayak trips
model.addConstr(TotalPeopleKayak == NumKayakTrips * PeoplePerKayak, name="kayak_people_relation")

# Add constraint to relate the total number of people transported by motorboat to the number of motorboat trips
TotalPeopleMotorboat_equation = (TotalPeopleMotorboat == NumMotorboatTrips * PeoplePerMotorboat)
model.addConstr(TotalPeopleMotorboat_equation, name="total_people_motorboat")

# Set objective
model.setObjective(NumKayakTrips * TimePerKayak + NumMotorboatTrips * TimePerMotorboat, gp.GRB.MINIMIZE)

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
