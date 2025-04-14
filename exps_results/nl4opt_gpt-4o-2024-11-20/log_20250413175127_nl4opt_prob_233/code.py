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
NumberHighVolumePipes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberHighVolumePipes")
NumberLowVolumePipes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberLowVolumePipes")
TotalPipes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalPipes")

# Add constraint to ensure the number of high-volume pipes is non-negative
model.addConstr(NumberHighVolumePipes >= 0, name="non_negative_high_volume_pipes")

# Ensure the number of low-volume pipes is non-negative
model.addConstr(NumberLowVolumePipes >= 0, name="non_negative_low_volume_pipes")

# Add total gas throughput constraint
model.addConstr(
    (NumberHighVolumePipes * HighVolumeCapacity) + (NumberLowVolumePipes * LowVolumeCapacity) >= Demand,
    name="total_gas_throughput_constraint"
)

# Add constraint on the total number of technicians required not exceeding the available technicians
model.addConstr(NumberHighVolumePipes * HighVolumeTechs + NumberLowVolumePipes * LowVolumeTechs <= TotalTechs, name="technician_availability")

# Add constraint ensuring at most MaxHighVolumePercent percent of total pipes are high-volume
model.addConstr(
    (1 - MaxHighVolumePercent) * NumberHighVolumePipes <= MaxHighVolumePercent * NumberLowVolumePipes,
    name="high_volume_pipe_limit"
)

# Add constraint ensuring the number of low-volume pipes used is at least the minimum required amount
model.addConstr(NumberLowVolumePipes >= MinLowVolumePipes, name="min_low_volume_pipes")

# Add constraint to ensure daily gas demand is satisfied
model.addConstr(
    HighVolumeCapacity * NumberHighVolumePipes + LowVolumeCapacity * NumberLowVolumePipes >= Demand, 
    name="daily_gas_demand"
)

# Add technician availability constraint
model.addConstr(
    HighVolumeTechs * NumberHighVolumePipes + LowVolumeTechs * NumberLowVolumePipes <= TotalTechs,
    name="technician_availability"
)

# Add constraint for high-volume pipes percentage
model.addConstr(
    NumberHighVolumePipes <= MaxHighVolumePercent * (NumberHighVolumePipes + NumberLowVolumePipes),
    name="high_volume_pipes_percentage"
)

# Add minimum low-volume pipes constraint
model.addConstr(NumberLowVolumePipes >= MinLowVolumePipes, name="min_low_volume_pipes")

# Set objective
model.setObjective(NumberHighVolumePipes + NumberLowVolumePipes, gp.GRB.MINIMIZE)

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
