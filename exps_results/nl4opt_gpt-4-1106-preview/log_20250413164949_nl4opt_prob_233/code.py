import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_233/data.json", "r") as f:
    data = json.load(f)

HighVolumeCapacity = data["HighVolumeCapacity"] # scalar parameter
HighVolumeTechs = data["HighVolumeTechs"] # scalar parameter
LowVolumeCapacity = data["LowVolumeCapacity"] # scalar parameter
LowVolumeTechs = data["LowVolumeTechs"] # scalar parameter
Demand = data["Demand"] # scalar parameter
TotalTechs = data["TotalTechs"] # scalar parameter
MaxHighVolumePercent = data["MaxHighVolumePercent"] # scalar parameter
MinLowVolumePipes = data["MinLowVolumePipes"] # scalar parameter
HighVolumePipes = model.addVar(vtype=gp.GRB.INTEGER, name="HighVolumePipes")
LowVolumePipes = model.addVar(vtype=gp.GRB.INTEGER, name="LowVolumePipes")

model.addConstr(HighVolumePipes >= 0, "high_volume_pipes_nonnegativity")

# Constraint: Number of low-volume pipes must be non-negative
model.addConstr(LowVolumePipes >= 0, name="LowVolumePipes_nonnegative")

# Add constraint for total gas throughput from all pipes to meet daily gas volume demand
model.addConstr(HighVolumePipes * HighVolumeCapacity + LowVolumePipes * LowVolumeCapacity >= Demand, name="throughput_demand")

# Add technician constraint
model.addConstr(HighVolumePipes * HighVolumeTechs + LowVolumePipes * LowVolumeTechs <= TotalTechs, name="techs_constraint")

# Add constraint to limit high-volume pipes to a maximum percentage of total pipes
model.addConstr(HighVolumePipes <= MaxHighVolumePercent * (HighVolumePipes + LowVolumePipes), "HighVolumePipes_max_percent")

# Add constraint for minimum number of low-volume pipes in operation
model.addConstr(LowVolumePipes >= MinLowVolumePipes, name="min_low_volume_pipes")

# Constraint: Total capacity must meet or exceed the daily gas demand
model.addConstr(HighVolumePipes * HighVolumeCapacity + LowVolumePipes * LowVolumeCapacity >= Demand, name="total_gas_capacity")

# Add constraint for total number of technicians not to exceed total available
model.addConstr(HighVolumePipes * HighVolumeTechs + LowVolumePipes * LowVolumeTechs <= TotalTechs, "TechniciansConstraint")

# Constraint: The number of high-volume pipes must not exceed 35% of the total number of pipes
model.addConstr(HighVolumePipes <= (HighVolumePipes + LowVolumePipes) * MaxHighVolumePercent, "high_volume_pipes_limit")

# Ensure the number of low-volume pipes is at least the minimum required
model.addConstr(LowVolumePipes >= MinLowVolumePipes, name="min_low_volume_pipes")

# Set objective
model.setObjective(HighVolumePipes + LowVolumePipes, gp.GRB.MINIMIZE)

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
