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
NumJugs = model.addVar(vtype=gp.GRB.INTEGER, name="NumJugs")
TotalUnitsSold = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalUnitsSold")

# Since NumSmallPackets is already defined as an integer variable, we just need to add a constraint to ensure it is non-negative
model.addConstr(NumSmallPackets >= 0, name="non_negative_NumSmallPackets")

# The number of jugs must be non-negative
model.addConstr(NumJugs >= 0, name="non_negative_jugs")

# Add constraint for total volume of jam not to exceed available volume
model.addConstr(NumSmallPackets * VolumeSmallPackets + NumJugs * VolumeJug <= TotalJam, name="volume_constraint")

# Add constraint to ensure the number of jugs is at least JugPacketRatio times as many as the number of sets of small packets
model.addConstr(NumJugs >= JugPacketRatio * NumSmallPackets, name="jugs_to_packets_ratio")

# Ensure that at least MinSmallPackets sets of small packets are filled
model.addConstr(NumSmallPackets >= MinSmallPackets, name="min_small_packets_constraint")

# Ensure the total volume of the small packets and jugs does not exceed the available total jam volume
model.addConstr(NumSmallPackets * VolumeSmallPackets + NumJugs * VolumeJug <= TotalJam, "VolumeConstraint")

# Proportional relation constraint between the number of jugs and the number of small packets
model.addConstr(NumJugs == JugPacketRatio * NumSmallPackets, name="jugs_to_packets_proportionality")

# Ensure the number of sets of small packets is not less than the minimum required
model.addConstr(NumSmallPackets >= MinSmallPackets, name="min_small_packets_constraint")

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
