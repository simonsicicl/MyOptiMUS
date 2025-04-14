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
AssignParticipantToCar = model.addVars(ParticipantNum, CarNum, vtype=gp.GRB.BINARY, name="AssignParticipantToCar")

# Each participant is assigned to at most one car
for i in range(ParticipantNum):
    model.addConstr(gp.quicksum(AssignParticipantToCar[i, j] for j in range(CarNum)) <= 1, name="participant_car_limit_{}".format(i))

# Constraint: A participant can only be assigned to a car if they are interested in it
for p in range(ParticipantNum):
    for c in range(CarNum):
        model.addConstr(AssignParticipantToCar[p,c] <= InterestMatrix[p,c], name=f"interest_constraint_p{p}_c{c}")

# Each participant can be assigned to at most one car
for i in range(ParticipantNum):
    model.addConstr(gp.quicksum(AssignParticipantToCar[i, j] for j in range(CarNum)) <= 1, name="participant_to_one_car_%d" % i)

# Each car can have at most one participant assigned
for j in range(CarNum):
    model.addConstr(gp.quicksum(AssignParticipantToCar[i, j] for i in range(ParticipantNum)) <= 1, name="one_participant_per_car_%d" % j)

# Set objective
model.setObjective(gp.quicksum(AssignParticipantToCar[p, c] for p in range(ParticipantNum) for c in range(CarNum)), gp.GRB.MAXIMIZE)

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
