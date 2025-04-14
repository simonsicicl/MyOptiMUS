import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_247/data.json", "r") as f:
    data = json.load(f)

VolumeSmallPackets = data["VolumeSmallPackets"] # scalar parameter
VolumeJug = data["VolumeJug"] # scalar parameter
JugPacketRatio = data["JugPacketRatio"] # scalar parameter
MinSmallPackets = data["MinSmallPackets"] # scalar parameter
TotalJam = data["TotalJam"] # scalar parameter
NumSmallPackets = model.addVar(vtype=gp.GRB.INTEGER, name="NumSmallPackets")
NumJugs = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumJugs")

# No additional code needed since NumSmallPackets is already defined as a non-negative integer variable

# Non-negativity constraint for NumJugs
model.addConstr(NumJugs >= 0, name="non_negative_NumJugs")

# Add constraint for total jam volume usage
model.addConstr(NumSmallPackets * VolumeSmallPackets + NumJugs * VolumeJug <= TotalJam, name="jam_volume_limit")

# Add constraint to ensure NumJugs is at least JugPacketRatio times NumSmallPackets
model.addConstr(NumJugs >= JugPacketRatio * NumSmallPackets, name="jugs_to_packets_ratio")

# Add constraint to ensure the minimum number of small packets allocated for jam filling
model.addConstr(NumSmallPackets >= MinSmallPackets, name="min_small_packets_constraint")

# Add constraint to ensure the number of jugs does not exceed the ratio of the number of small packet sets
model.addConstr(NumJugs <= JugPacketRatio * NumSmallPackets, name="limit_num_jugs_by_packet_ratio")

# Add constraint to ensure the minimum number of small packet sets
model.addConstr(NumSmallPackets >= MinSmallPackets, name="min_small_packets")

# Set objective
model.setObjective(NumSmallPackets + NumJugs, gp.GRB.MAXIMIZE)

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
