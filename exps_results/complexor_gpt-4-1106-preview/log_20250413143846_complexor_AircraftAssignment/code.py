import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/AircraftAssignment/data.json", "r") as f:
    data = json.load(f)

TotalAircraft = data["TotalAircraft"] # scalar parameter
TotalRoutes = data["TotalRoutes"] # scalar parameter
Availability = np.array(data["Availability"]) # ['TotalAircraft']
Demand = np.array(data["Demand"]) # ['TotalRoutes']
Capacity = np.array(data["Capacity"]) # ['TotalAircraft', 'TotalRoutes']
Costs = np.array(data["Costs"]) # ['TotalAircraft', 'TotalRoutes']
AircraftAssignment = model.addVars(TotalAircraft, TotalRoutes, vtype=gp.GRB.BINARY, name="AircraftAssignment")

# Add constraints for aircraft availability
for i in range(TotalAircraft):
    model.addConstr(gp.quicksum(AircraftAssignment[i, j] for j in range(TotalRoutes)) <= Availability[i], name=f"aircraft_availability_{i}")

# Each route must have at least the required number of aircraft to meet its demand
for j in range(TotalRoutes):
    model.addConstr(gp.quicksum(AircraftAssignment[i, j] for i in range(TotalAircraft)) >= Demand[j], name=f"demand_route_{j}")

# Ensure an aircraft is assigned to a route only if it has the capacity
for i in range(TotalAircraft):
    for j in range(TotalRoutes):
        model.addConstr(AircraftAssignment[i, j] <= Capacity[i, j], name=f"AircraftCapacity_{i}_{j}")

# Add constraints to ensure the number of aircraft assigned to each route is an integer value equal to the demand
for j in range(TotalRoutes):
    model.addConstr(
        gp.quicksum(AircraftAssignment[i, j] for i in range(TotalAircraft)) == Demand[j],
        name=f"demand_route_{j}"
    )

# Since AircraftAssignment is defined as a binary variable, AircraftAssignment_ij >= 0 is inherent to the definition and no code is needed for this constraint.
# Binary variables in Gurobi are by definition in {0,1}, which satisfies the non-negativity constraint.

# Ensure the total number of aircraft assigned does not exceed the total available aircraft
model.addConstr(gp.quicksum(AircraftAssignment[i, j] for i in range(TotalAircraft) for j in range(TotalRoutes)) <= TotalAircraft, name="total_aircraft_assignment")

# Ensure that each aircraft does not exceed its availability
for i in range(TotalAircraft):
    model.addConstr(gp.quicksum(AircraftAssignment[i, j] for j in range(TotalRoutes)) <= Availability[i], name=f"aircraft_availability_{i}")

# Ensure that the demand for each route is exactly met
for j in range(TotalRoutes):
    model.addConstr(gp.quicksum(AircraftAssignment[i, j] for i in range(TotalAircraft)) == Demand[j], name=f"Demand_meet_route_{j}")

# Ensure that aircrafts are only assigned to routes if they have the capacity for it
for i in range(TotalAircraft):
    for j in range(TotalRoutes):
        model.addConstr(AircraftAssignment[i,j] <= Capacity[i,j], name=f"AircraftAssignment_capacity_{i}_{j}")

# Set objective
model.setObjective(gp.quicksum(Costs[i, j] * AircraftAssignment[i, j] for i in range(TotalAircraft) for j in range(TotalRoutes)), gp.GRB.MINIMIZE)

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
