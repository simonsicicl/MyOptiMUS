import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/Flowshop_2/data.json", "r") as f:
    data = json.load(f)

JobCount = data["JobCount"] # scalar parameter
MachineCount = data["MachineCount"] # scalar parameter
ProcessingTime = np.array(data["ProcessingTime"]) # ['JobCount', 'MachineCount']
JobStartTimes = model.addVars(JobCount, MachineCount, vtype=gp.GRB.CONTINUOUS, name="JobStartTimes")
MachineSequenceOrder = model.addVars(JobCount, JobCount, MachineCount, vtype=gp.GRB.BINARY, name="MachineSequenceOrder")
Makespan = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Makespan")

# Add sequential processing constraints across machines
for j in range(JobCount):
    for m in range(MachineCount - 1):
        model.addConstr(
            JobStartTimes[j, m + 1] >= JobStartTimes[j, m] + ProcessingTime[j, m],
            name=f"sequential_processing_{j}_{m}"
        )

# Add constraints to ensure that each machine processes only one job at a time
M = 1e6  # Large constant value for big-M formulation
for m in range(MachineCount):
    for j1 in range(JobCount):
        for j2 in range(JobCount):
            if j1 != j2:
                model.addConstr(
                    JobStartTimes[j1, m] + ProcessingTime[j1, m] 
                    <= JobStartTimes[j2, m] + M * (1 - MachineSequenceOrder[j1, j2, m]),
                    name=f"MachineOneJob_{j1}_{j2}_{m}_1"
                )
                model.addConstr(
                    JobStartTimes[j2, m] + ProcessingTime[j2, m] 
                    <= JobStartTimes[j1, m] + M * (1 - MachineSequenceOrder[j2, j1, m]),
                    name=f"MachineOneJob_{j1}_{j2}_{m}_2"
                )

# Add constraints to ensure jobs on the same machine do not overlap
for j in range(JobCount):
    for j_prime in range(JobCount):
        if j != j_prime:  # Ensure we are comparing two different jobs
            for m in range(MachineCount):
                model.addConstr(
                    JobStartTimes[j_prime, m] >= JobStartTimes[j, m] + ProcessingTime[j, m] - (1 - MachineSequenceOrder[j, j_prime, m]) * M,
                    name=f"job_non_overlap_{j}_{j_prime}_machine_{m}"
                )

# Add binary variable sequencing constraints for job order on each machine
for m in range(MachineCount):
    for j in range(JobCount):
        for j_prime in range(JobCount):
            if j != j_prime:
                model.addConstr(
                    MachineSequenceOrder[j, j_prime, m] + MachineSequenceOrder[j_prime, j, m] == 1,
                    name=f"seq_order_{j}_{j_prime}_{m}"
                )

# Add sequencing constraints to ensure each pair of jobs has exactly one sequencing order on each machine
for j1 in range(JobCount):
    for j2 in range(JobCount):
        if j1 != j2:  # Ensuring j1 and j2 are distinct jobs
            for m in range(MachineCount):
                model.addConstr(MachineSequenceOrder[j1, j2, m] + MachineSequenceOrder[j2, j1, m] == 1, 
                                name=f"seq_order_j{j1}_j{j2}_m{m}")

# Add constraint to ensure Makespan is greater than or equal to the completion time of all jobs on the last machine
for j in range(JobCount):
    model.addConstr(Makespan >= JobStartTimes[j, MachineCount - 1] + ProcessingTime[j, MachineCount - 1], name=f"MakespanConstraint_job{j}")

# Set objective
model.setObjective(Makespan, gp.GRB.MINIMIZE)

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
