import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/2/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
IsWorkstation = np.array(data["IsWorkstation"]) # ['N']
Price = np.array(data["Price"]) # ['N']
DiskDrives = np.array(data["DiskDrives"]) # ['N']
MemoryBoards = np.array(data["MemoryBoards"]) # ['N']
MaxCpu = data["MaxCpu"] # scalar parameter
MinDisk = data["MinDisk"] # scalar parameter
MaxDisk = data["MaxDisk"] # scalar parameter
MinMemory = data["MinMemory"] # scalar parameter
MaxMemory = data["MaxMemory"] # scalar parameter
Demand = np.array(data["Demand"]) # ['N']
DemandGP = data["DemandGP"] # scalar parameter
DemandWS = data["DemandWS"] # scalar parameter
Preorder = np.array(data["Preorder"]) # ['N']
AltMemory = data["AltMemory"] # scalar parameter
AltCompatible = np.array(data["AltCompatible"]) # ['N']
SystemsProduced = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="SystemsProduced")
IsProducedWorkstation = model.addVars(N, vtype=gp.GRB.BINARY, name="IsProducedWorkstation")
IsCompatible = model.addVars(N, vtype=gp.GRB.BINARY, name="IsCompatible")
IsCompatible = model.addVars(N, vtype=gp.GRB.BINARY, name="IsCompatible")

# Modify variable type to integer for non-negativity and integrality
for i in range(N):
    SystemsProduced[i].vtype = gp.GRB.INTEGER

# Add constraints for restricting production based on system type
M = 1e6  # Set a sufficiently large constant value for M
for i in range(N):
    if IsWorkstation[i] == 1:
        model.addConstr(SystemsProduced[i] <= M * IsProducedWorkstation[i], name=f"workstation_limit_{i}")
    else:
        model.addConstr(SystemsProduced[i] <= M * (1 - IsProducedWorkstation[i]), name=f"general_system_limit_{i}")

# Add system production limit constraint
model.addConstr(gp.quicksum(SystemsProduced[i] for i in range(N)) <= MaxCpu, name="production_limit")

# Add constraints for the total number of disk drives
model.addConstr(
    gp.quicksum(SystemsProduced[i] * DiskDrives[i] for i in range(N)) >= MinDisk,
    name="min_disk_constraint"
)
model.addConstr(
    gp.quicksum(SystemsProduced[i] * DiskDrives[i] for i in range(N)) <= MaxDisk,
    name="max_disk_constraint"
)

# Add constraint for total number of 256K memory boards
model.addConstr(
    gp.quicksum(SystemsProduced[i] * MemoryBoards[i] for i in range(N)) >= MinMemory,
    name="min_memory_constraint"
)
model.addConstr(
    gp.quicksum(SystemsProduced[i] * MemoryBoards[i] for i in range(N)) <= MaxMemory,
    name="max_memory_constraint"
)

# Add production-demand constraints
for i in range(N):
    model.addConstr(SystemsProduced[i] <= Demand[i], name=f"production_demand_constraint_{i}")

# Add constraint for total production of general-purpose systems
model.addConstr(
    gp.quicksum((1 - IsWorkstation[i]) * SystemsProduced[i] for i in range(N)) <= DemandGP,
    name="Production_GP_Constraint"
)

# Add constraint ensuring total workstation production does not exceed DemandWS
model.addConstr(
    gp.quicksum(SystemsProduced[i] * IsWorkstation[i] for i in range(N)) <= DemandWS,
    name="workstation_demand_constraint"
)

# Add preorder fulfillment constraints
for i in range(N):
    model.addConstr(SystemsProduced[i] >= Preorder[i], name=f"Preorder_Fulfillment_{i}")

# Add constraints to ensure systems are configured with compatible alternative memory
M = 1e6  # Large constant to implement the big-M method
for i in range(N):
    model.addConstr(SystemsProduced[i] <= M * IsCompatible[i], name=f"compatibility_constraint_{i}")

# Add constraint to limit the total number of systems with alternative memory
model.addConstr(gp.quicksum(IsCompatible[i] for i in range(N)) <= AltMemory, name="AltMemoryLimit")

# No additional constraint code needed because the variable "IsProducedWorkstation" has already been defined as binary.

# Add compatibility constraints
for i in range(N):
    model.addConstr(IsCompatible[i] <= AltCompatible[i], name=f"compatibility_constraint_{i}")

# Add compatibility constraints
for i in range(N):
    model.addConstr(IsCompatible[i] <= AltCompatible[i], name=f"compatibility_constraint_{i}")

# Set objective
model.setObjective(gp.quicksum(SystemsProduced[i] * Price[i] for i in range(N)), gp.GRB.MAXIMIZE)

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
