import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/CarSelection/data.json", "r") as f:
    data = json.load(f)

ParticipantNum = data["ParticipantNum"] # scalar parameter
CarNum = data["CarNum"] # scalar parameter
InterestMatrix = np.array(data["InterestMatrix"]) # ['ParticipantNum', 'CarNum']
AssignedMatrix = model.addVars(ParticipantNum, CarNum, vtype=gp.GRB.BINARY, name="AssignedMatrix")

# Add constraint to ensure each participant is assigned to at most one car
for p in range(ParticipantNum):
    model.addConstr(gp.quicksum(AssignedMatrix[p, c] for c in range(CarNum)) <= 1, name=f"participant_assignment_{p}")

# Add constraint: A participant can be assigned to a car only if they are interested in that car
for p in range(ParticipantNum):
    for c in range(CarNum):
        model.addConstr(AssignedMatrix[p, c] <= InterestMatrix[p, c], name=f"assignment_interest_{p}_{c}")

# No additional constraints are required as the integrality of AssignedMatrix is already determined as binary using gp.GRB.BINARY.

# Add constraints to ensure participants are only assigned to cars they are interested in
for p in range(ParticipantNum):
    for c in range(CarNum):
        model.addConstr(AssignedMatrix[p, c] <= InterestMatrix[p, c], name=f"interest_constraint_p{p}_c{c}")

# Ensure participants are assigned only to cars they are interested in
for i in range(ParticipantNum):
    for j in range(CarNum):
        model.addConstr(AssignedMatrix[i, j] <= InterestMatrix[i, j], name=f"interest_constraint_{i}_{j}")

# Set objective
model.setObjective(gp.quicksum(InterestMatrix[i, j] * AssignedMatrix[i, j] for i in range(ParticipantNum) for j in range(CarNum)), gp.GRB.MAXIMIZE)

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
