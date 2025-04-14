import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/65/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
IsolateCentral = np.array(data["IsolateCentral"]) # ['N']
ScanCentral = np.array(data["ScanCentral"]) # ['N']
IsolateDistributed = np.array(data["IsolateDistributed"]) # ['N']
ScanDistributed = np.array(data["ScanDistributed"]) # ['N']
CentralCost = data["CentralCost"] # scalar parameter
DistributedCost = data["DistributedCost"] # scalar parameter
CentralMaxHours = data["CentralMaxHours"] # scalar parameter
DistributedMaxHours = data["DistributedMaxHours"] # scalar parameter
InterventionSelected = model.addVars(N, vtype=gp.GRB.BINARY, name="InterventionSelected")
CentralInterventionsCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="CentralInterventionsCount")
DistributedInterventionsCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DistributedInterventionsCount")

# Add constraint for total processing time at central system
model.addConstr(
    gp.quicksum(IsolateCentral[i] * InterventionSelected[i] for i in range(N)) <= CentralMaxHours,
    name="central_processing_time_limit"
)

# Add total scanning time constraint at the central system
model.addConstr(gp.quicksum(ScanCentral[i] * InterventionSelected[i] for i in range(N)) <= CentralMaxHours, name="central_scanning_time_limit")

# Adding constraint for total distributed processing time
model.addConstr(
    gp.quicksum(IsolateDistributed[i] * InterventionSelected[i] for i in range(N)) <= DistributedMaxHours,
    name="distributed_time_limit"
)

# Add constraint for distributed system maximum processing time
model.addConstr(
    gp.quicksum(ScanDistributed[i] * InterventionSelected[i] for i in range(N)) <= DistributedMaxHours,
    name="DistributedScanningConstraint"
)

# Add constraint to ensure the total number of selected interventions equals N
model.addConstr(gp.quicksum(InterventionSelected[i] for i in range(N)) == N, name="total_selected_interventions")

# Ensure CentralInterventionsCount is non-negative and integer
CentralInterventionsCount.vtype = gp.GRB.INTEGER
model.addConstr(CentralInterventionsCount >= 0, name="non_negative_CentralInterventionsCount")

# Change variable's type to integer and ensure non-negativity
DistributedInterventionsCount.vtype = gp.GRB.INTEGER
DistributedInterventionsCount.lb = 0

# Add constraint for the total count of central system interventions
model.addConstr(CentralInterventionsCount == gp.quicksum(InterventionSelected[i] for i in range(N)), name="central_interventions_count")

# Add central system processing time constraint
model.addConstr(
    gp.quicksum(
        InterventionSelected[i] * (IsolateCentral[i] + ScanCentral[i])
        for i in range(N)
    ) <= CentralMaxHours,
    name="central_system_processing_time"
)

# Add constraint to ensure total processing time does not exceed maximum allowed hours
model.addConstr(
    gp.quicksum(
        InterventionSelected[i] * (IsolateDistributed[i] + ScanDistributed[i])
        for i in range(N)
    ) <= DistributedMaxHours,
    name="total_processing_time_limit"
)

# Add constraint for the total number of interventions processed
model.addConstr(CentralInterventionsCount == gp.quicksum(InterventionSelected[i] for i in range(N)), name="total_interventions_constraint")

# Add constraint for DistributedInterventionsCount
model.addConstr(
    DistributedInterventionsCount == gp.quicksum(InterventionSelected[i] for i in range(N)),
    name="TotalDistributedInterventions"
)

# Set objective
model.setObjective(CentralCost * CentralInterventionsCount + DistributedCost * DistributedInterventionsCount, gp.GRB.MINIMIZE)

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
