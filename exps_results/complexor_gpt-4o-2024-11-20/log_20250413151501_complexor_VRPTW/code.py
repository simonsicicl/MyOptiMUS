import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/VRPTW/data.json", "r") as f:
    data = json.load(f)

CustomerCount = data["CustomerCount"] # scalar parameter
VehicleCount = data["VehicleCount"] # scalar parameter
CustomerDemand = np.array(data["CustomerDemand"]) # ['CustomerCount']
CustomerLBTW = np.array(data["CustomerLBTW"]) # ['CustomerCount']
CustomerUBTW = np.array(data["CustomerUBTW"]) # ['CustomerCount']
CustomerDistance = np.array(data["CustomerDistance"]) # ['CustomerCount', 'CustomerCount']
CustomerServiceTime = np.array(data["CustomerServiceTime"]) # ['CustomerCount']
VehicleCapacity = np.array(data["VehicleCapacity"]) # ['VehicleCount']
CustomerAssigned = model.addVars(VehicleCount, CustomerCount, vtype=gp.GRB.BINARY, name="CustomerAssigned")
CustomerServiceStartTime = model.addVars(CustomerCount, vtype=gp.GRB.CONTINUOUS, name="CustomerServiceStartTime")
VehicleUsed = model.addVars(VehicleCount, vtype=gp.GRB.BINARY, name="VehicleUsed")
RouteConnection = model.addVars(CustomerCount, CustomerCount, vtype=gp.GRB.BINARY, name="RouteConnection")

# Add vehicle capacity constraints
for i in range(VehicleCount):
    model.addConstr(
        gp.quicksum(CustomerAssigned[i, j] * CustomerDemand[j] for j in range(CustomerCount)) <= VehicleCapacity[i],
        name=f"vehicle_capacity_{i}"
    )

# Add time window constraints for each customer
for j in range(CustomerCount):
    model.addConstr(CustomerLBTW[j] <= CustomerServiceStartTime[j], name=f"CustomerStartTimeLB_{j}")
    model.addConstr(CustomerServiceStartTime[j] <= CustomerUBTW[j], name=f"CustomerStartTimeUB_{j}")

# Add constraint to limit the number of vehicles used
model.addConstr(gp.quicksum(VehicleUsed[i] for i in range(VehicleCount)) <= VehicleCount, name="vehicle_limit")

# No additional code needed. The integrality of CustomerAssigned is already correctly set as binary in its variable definition.

# Add time propagation constraints to ensure service sequencing respects travel and service times
for j in range(CustomerCount):
    for k in range(CustomerCount):
        if j != k:
            model.addConstr(
                CustomerServiceStartTime[k] >= CustomerServiceStartTime[j] + CustomerServiceTime[j] + CustomerDistance[j, k],
                name=f"time_propagation_{j}_{k}"
            )

# Add constraints to ensure VehicleUsed is activated only if at least one customer is assigned to the vehicle
for i in range(VehicleCount):
    model.addConstr(gp.quicksum(CustomerAssigned[i, j] for j in range(CustomerCount)) <= CustomerCount * VehicleUsed[i], name=f"vehicle_activation_{i}")

# Add route connection constraints to ensure a route exists only if both customers are visited by the same vehicle
for j in range(CustomerCount):
    for k in range(CustomerCount):
        model.addConstr(
            RouteConnection[j, k] <= gp.quicksum(CustomerAssigned[i, j] * CustomerAssigned[i, k] for i in range(VehicleCount)),
            name=f"route_connection_{j}_{k}"
        )

# Add constraints to ensure each customer is visited exactly once by any vehicle
for j in range(CustomerCount):
    model.addConstr(gp.quicksum(CustomerAssigned[i, j] for i in range(VehicleCount)) == 1, name=f"visit_customer_once_{j}")

# Add vehicle capacity constraints
for i in range(VehicleCount):
    model.addConstr(
        gp.quicksum(CustomerAssigned[i, j] * CustomerDemand[j] for j in range(CustomerCount)) 
        <= VehicleCapacity[i],
        name=f"vehicle_capacity_{i}"
    )

# Add time window constraints for customer service start times
for j in range(CustomerCount):
    model.addConstr(CustomerLBTW[j] <= CustomerServiceStartTime[j], name=f"CustomerServiceStartTime_LB_{j}")
    model.addConstr(CustomerServiceStartTime[j] <= CustomerUBTW[j], name=f"CustomerServiceStartTime_UB_{j}")

# Add constraints to ensure service start time accounts for travel time
M = 1e6  # A large constant (big-M method)
for j in range(CustomerCount):
    for k in range(CustomerCount):
        if j != k:
            model.addConstr(
                CustomerServiceStartTime[k] >= CustomerServiceStartTime[j] 
                + CustomerServiceTime[j] 
                + CustomerDistance[j, k] * RouteConnection[j, k]
                - M * (1 - RouteConnection[j, k]),
                name=f"service_start_time_{j}_{k}"
            )

# Set objective
model.setObjective(gp.quicksum(CustomerDistance[j, k] * RouteConnection[j, k] for i in range(VehicleCount) for j in range(CustomerCount) for k in range(CustomerCount)), gp.GRB.MINIMIZE)

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
