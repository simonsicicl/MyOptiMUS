import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_251/data.json", "r") as f:
    data = json.load(f)

FreightCapacity = data["FreightCapacity"] # scalar parameter
AirCapacity = data["AirCapacity"] # scalar parameter
FreightCost = data["FreightCost"] # scalar parameter
AirCost = data["AirCost"] # scalar parameter
MinimumTons = data["MinimumTons"] # scalar parameter
Budget = data["Budget"] # scalar parameter
AirFraction = data["AirFraction"] # scalar parameter
MinimumFreightTrips = data["MinimumFreightTrips"] # scalar parameter
FreightTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FreightTrips")
AirTrips = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AirTrips")
TonsTransportedByAir = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TonsTransportedByAir")

# Ensure the total tons of candles transported meet or exceed the minimum required
model.addConstr(FreightCapacity * FreightTrips + AirCapacity * AirTrips >= MinimumTons, name="min_tons_transported")

# Since FreightTrips is already defined as a continuous variable, we just need to add a constraint ensuring it's non-negative
model.addConstr(FreightTrips >= 0, "FreightTrips_non_negative")

# Air trips non-negativity constraint
model.addConstr(AirTrips >= 0, name="non_negative_air_trips")

# Total cost of transportation should not exceed the budget
model.addConstr(FreightTrips * FreightCost + AirTrips * AirCost <= Budget, name="transportation_budget")

# At least AirFraction of the total tons must be transported by air constraint
model.addConstr(TonsTransportedByAir >= AirFraction * MinimumTons, name="air_transport_fraction")

# Total tons transported by air equals air trips times air capacity constraint
model.addConstr(TonsTransportedByAir == AirTrips * AirCapacity, name="air_transport_capacity")

# Ensure the total tons transported meets the minimum requirement
model.addConstr(FreightTrips * FreightCapacity + AirTrips * AirCapacity >= MinimumTons, "min_tons_transported")

# Ensure that the budget is not exceeded
model.addConstr(FreightTrips * FreightCost + AirTrips * AirCost <= Budget, name="budget_constraint")

# Ensure that at least a certain fraction of the total tons is transported by air
model.addConstr(TonsTransportedByAir >= AirFraction * MinimumTons, name="air_transport_fraction")

# Relate the tons transported by air to the air trips and air capacity
model.addConstr(TonsTransportedByAir == AirTrips * AirCapacity, name="relate_tons_to_trips_and_capacity")

# Ensure the minimum number of freight trips is met
model.addConstr(FreightTrips >= MinimumFreightTrips, name="min_freight_trips_constraint")

# Set objective
model.setObjective(FreightTrips + AirTrips, gp.GRB.MINIMIZE)

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
