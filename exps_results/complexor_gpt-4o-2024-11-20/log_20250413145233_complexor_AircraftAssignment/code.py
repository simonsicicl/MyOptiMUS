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
Assignment = model.addVars(TotalAircraft, TotalRoutes, vtype=gp.GRB.BINARY, name="Assignment")
TotalAssigned = model.addVars(TotalRoutes, vtype=gp.GRB.INTEGER, name="TotalAssigned")

# Add aircraft availability constraints
for i in range(TotalAircraft):
    model.addConstr(gp.quicksum(Assignment[i, j] for j in range(TotalRoutes)) <= Availability[i], name=f"aircraft_availability_{i}")

# Add route demand satisfaction constraints
for r in range(TotalRoutes):
    model.addConstr(gp.quicksum(Assignment[a, r] for a in range(TotalAircraft)) >= Demand[r], 
                    name=f"route_demand_{r}")

# Add aircraft assignment capacity constraints
for i in range(TotalAircraft):
    for j in range(TotalRoutes):
        model.addConstr(Assignment[i, j] <= Capacity[i, j], name=f"aircraft_capacity_{i}_{j}")

# The integrality of Assignment is inherently handled as it is defined as a binary variable. No additional code is required.

# Add non-negativity constraint for TotalAssigned to each route
for j in range(TotalRoutes):
    model.addConstr(TotalAssigned[j] >= 0, name=f"nonnegativity_TotalAssigned_{j}")

# Add constraint to ensure the total number of aircraft assigned does not exceed the total available aircraft
model.addConstr(
    gp.quicksum(Assignment[i, j] for i in range(TotalAircraft) for j in range(TotalRoutes)) <= TotalAircraft,
    name="aircraft_assignment_limit"
)

# No additional code needed: decision variable Assignment was already declared as binary.

# Add constraints ensuring the total number of aircraft assigned to each route equals the respective integer variable TotalAssigned
for j in range(TotalRoutes):
    model.addConstr(TotalAssigned[j] == gp.quicksum(Assignment[i, j] for i in range(TotalAircraft)), name=f"TotalAssigned_route{j}")

# Add constraints to relate Assignment and TotalAssigned
for j in range(TotalRoutes):
    model.addConstr(TotalAssigned[j] == gp.quicksum(Assignment[i, j] for i in range(TotalAircraft)), 
                    name=f"Total_Assigned_to_Route_{j}")

# Add aircraft availability constraints
for i in range(TotalAircraft):
    model.addConstr(
        gp.quicksum(Assignment[i, j] for j in range(TotalRoutes)) <= Availability[i], 
        name=f"aircraft_availability_{i}"
    )

# Add constraints to ensure each route meets its aircraft demand
for j in range(TotalRoutes):
    model.addConstr(
        gp.quicksum(Assignment[i, j] for i in range(TotalAircraft)) == Demand[j], 
        name=f"route_demand_{j}"
    )

# Add capacity feasibility constraints for aircraft assignment
for i in range(TotalAircraft):
    for j in range(TotalRoutes):
        model.addConstr(Assignment[i, j] <= Capacity[i, j], name=f"capacity_feasibility_aircraft_{i}_route_{j}")

# Set objective
model.setObjective(gp.quicksum(Costs[i, j] * Assignment[i, j] for i in range(TotalAircraft) for j in range(TotalRoutes)), gp.GRB.MINIMIZE)

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
