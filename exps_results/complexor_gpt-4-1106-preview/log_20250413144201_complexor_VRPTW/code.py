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
CustomerServedByVehicle = model.addVars(VehicleCount, CustomerCount, vtype=gp.GRB.BINARY, name="CustomerServedByVehicle")
ArrivalTime = model.addVars(VehicleCount, CustomerCount, vtype=gp.GRB.CONTINUOUS, name="ArrivalTime")
VehicleUsed = model.addVars(VehicleCount, vtype=gp.GRB.BINARY, name="VehicleUsed")
VehicleDirectTravel = model.addVars(VehicleCount, CustomerCount, CustomerCount, vtype=gp.GRB.BINARY, name="VehicleDirectTravel")

# Add vehicle capacity constraints
for i in range(VehicleCount):
    model.addConstr(gp.quicksum(CustomerDemand[j] * CustomerServedByVehicle[i, j] for j in range(CustomerCount)) <= VehicleCapacity[i], name="vehicle_capacity_{}".format(i))

# Ensure each customer is served within their time window
for j in range(CustomerCount):
    model.addConstr(
        gp.quicksum(CustomerServedByVehicle[i, j] * ArrivalTime[i, j] for i in range(VehicleCount)) >= CustomerLBTW[j],
        name=f"time_window_constr_for_customer_{j}"
    )

# Ensure the total used vehicles do not exceed the number of vehicles available
model.addConstr(gp.quicksum(VehicleUsed[i] for i in range(VehicleCount)) <= VehicleCount, name="vehicle_limit")

# Add constraints for arrival time to be less than or equal to customer's time window upper bound if served
for j in range(CustomerCount):
    for i in range(VehicleCount):
        model.addConstr(CustomerServedByVehicle[i, j] * ArrivalTime[i, j] <= CustomerUBTW[j], 
                        name="cust_time_window_ub_{}_{}".format(i, j))

# Define the constraint that a vehicle is considered used if it serves at least one customer
for i in range(VehicleCount):
    for j in range(CustomerCount):
        model.addConstr(VehicleUsed[i] >= CustomerServedByVehicle[i, j], name=f"vehicle_usage_{i}_{j}")

CustomerServedByVehicle = model.addVars(VehicleCount, CustomerCount, vtype=gp.GRB.BINARY, name='CustomerServedByVehicle')
ArrivalTime = model.addVars(VehicleCount, CustomerCount, vtype=gp.GRB.CONTINUOUS, name='ArrivalTime')
VehicleUsed = model.addVars(VehicleCount, vtype=gp.GRB.BINARY, name='VehicleUsed')

# Set objective
model.setObjective(
    gp.quicksum(
        CustomerServedByVehicle[i, j] * 
        CustomerServedByVehicle[i, k] * 
        CustomerDistance[j, k]
        for i in range(VehicleCount)
        for j in range(CustomerCount)
        for k in range(CustomerCount) if j != k
    ),
    gp.GRB.MINIMIZE
)

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
