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
TonsByFreight = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TonsByFreight")
TonsByAir = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TonsByAir")

# Add constraint for the minimum total tons of candles to be transported
model.addConstr(
    FreightTrips * FreightCapacity + AirTrips * AirCapacity >= MinimumTons,
    name="min_candles_transport",
)

# The non-negativity of FreightTrips is already enforced by defining it as a continuous variable, no additional constraint is needed.

# The variable "AirTrips" is already coded as a non-negative continuous variable using the "gp.GRB.CONTINUOUS" type. No additional constraint code is needed.

# Add transportation cost constraint
model.addConstr(FreightCost * FreightTrips + AirCost * AirTrips <= Budget, name="transportation_budget_constraint")

# Add air transportation fraction constraint
model.addConstr(TonsByAir >= AirFraction * (TonsByFreight + TonsByAir), name="air_transportation_fraction")

# Add constraint linking TonsByFreight, FreightTrips, and FreightCapacity
model.addConstr(TonsByFreight == FreightTrips * FreightCapacity, name="link_tons_by_freight")

# Add constraint linking TonsByAir to AirTrips and AirCapacity
model.addConstr(TonsByAir == AirTrips * AirCapacity, name="link_TonsByAir_AirTrips_AirCapacity")

# Add constraint: Total tons transported by freight cannot exceed freight capacity per trip multiplied by the number of freight trips
model.addConstr(TonsByFreight <= FreightCapacity * FreightTrips, name="freight_transport_capacity")

# Adding constraint to ensure total tons by air do not exceed air capacity per trip multiplied by air trips
model.addConstr(TonsByAir <= AirCapacity * AirTrips, name="air_transport_capacity_constraint")

# Add total transportation constraint
model.addConstr(TonsByFreight + TonsByAir >= MinimumTons, name="total_transportation")

# Add transportation cost constraint
model.addConstr(FreightCost * FreightTrips + AirCost * AirTrips <= Budget, name="transportation_cost_limit")

# Add constraint ensuring at least a fraction of the total tons is transported by air
model.addConstr(TonsByAir >= AirFraction * (TonsByFreight + TonsByAir), name="air_transport_fraction")

# Add constraint to ensure the number of freight trips meets the minimum required freight trips
model.addConstr(FreightTrips >= MinimumFreightTrips, name="freight_trips_minimum")

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
