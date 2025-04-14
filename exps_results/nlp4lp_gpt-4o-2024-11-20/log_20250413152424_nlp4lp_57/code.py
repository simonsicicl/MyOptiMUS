import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/57/data.json", "r") as f:
    data = json.load(f)

NumMachines = data["NumMachines"] # scalar parameter
NumParts = data["NumParts"] # scalar parameter
TimeRequired = np.array(data["TimeRequired"]) # ['NumMachines', 'NumParts']
MachineCosts = np.array(data["MachineCosts"]) # ['NumMachines']
Availability = np.array(data["Availability"]) # ['NumMachines']
Prices = np.array(data["Prices"]) # ['NumParts']
MinBatches = np.array(data["MinBatches"]) # ['NumParts']
StandardCost = data["StandardCost"] # scalar parameter
OvertimeCost = data["OvertimeCost"] # scalar parameter
OvertimeHour = np.array(data["OvertimeHour"]) # ['NumMachines']
BatchesProduced = model.addVars(NumParts, vtype=gp.GRB.CONTINUOUS, name="BatchesProduced")
TotalTimeUsed = model.addVars(NumMachines, vtype=gp.GRB.CONTINUOUS, name="TotalTimeUsed")
OvertimeHoursUsed = model.addVars(NumMachines, vtype=gp.GRB.CONTINUOUS, name="OvertimeHoursUsed")
TotalTimeUsed = model.addVars(NumMachines, vtype=gp.GRB.CONTINUOUS, name="TotalTimeUsed")
OvertimeHoursUsed = model.addVars(NumMachines, vtype=gp.GRB.CONTINUOUS, name="OvertimeHoursUsed")

# Add machine time availability constraints
for m in range(NumMachines):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(NumParts)) <= Availability[m],
        name=f"machine_time_availability_{m}"
    )

# Add production time constraints for each machine
for m in range(NumMachines):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(NumParts))
        <= Availability[m],
        name=f"production_time_machine_{m}"
    )

# Add minimum batch production constraints
for p in range(NumParts):
    model.addConstr(BatchesProduced[p] >= MinBatches[p], name=f"min_batches_part_{p}")

# Add constraints to ensure total time used by each machine does not exceed availability and overtime
for m in range(NumMachines):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(NumParts)) <= Availability[m] + OvertimeHour[m],
        name=f"time_constraint_machine_{m}"
    )

# Add non-negativity constraints for the number of batches produced
for p in range(NumParts):
    model.addConstr(BatchesProduced[p] >= 0, name=f"non_negativity_BatchesProduced_{p}")

# Add TotalTimeUsed constraints for each machine
for m in range(NumMachines):
    model.addConstr(
        TotalTimeUsed[m] == gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(NumParts)),
        name=f"TotalTimeUsed_machine_{m}"
    )

# Add overtime hours constraints
for m in range(NumMachines):
    model.addConstr(OvertimeHoursUsed[m] >= TotalTimeUsed[m] - Availability[m], name=f"OvertimeHours_constraint_{m}")

# Add non-negativity constraint for OvertimeHoursUsed
for m in range(NumMachines):
    model.addConstr(OvertimeHoursUsed[m] >= 0, name=f"non_negative_overtime_{m}")

# Add constraints to compute TotalTimeUsed for each machine
for m in range(NumMachines):
    model.addConstr(
        TotalTimeUsed[m] == gp.quicksum(BatchesProduced[p] * TimeRequired[m, p] for p in range(NumParts)),
        name=f"TotalTimeUsed_constraint_machine_{m}"
    )

# Add constraint to define OvertimeHoursUsed for each machine
for m in range(NumMachines):
    model.addConstr(OvertimeHoursUsed[m] >= TotalTimeUsed[m] - Availability[m], name=f"overtime_def_1_{m}")
    model.addConstr(OvertimeHoursUsed[m] >= 0, name=f"overtime_def_2_{m}")

# Add constraints to enforce minimum production requirements
for p in range(NumParts):
    model.addConstr(BatchesProduced[p] >= MinBatches[p], name=f"min_production_part_{p}")

# Add constraints to limit overtime hours used to the maximum allowable hours for each machine
for m in range(NumMachines):
    model.addConstr(OvertimeHoursUsed[m] <= OvertimeHour[m], name=f"OvertimeLimit_machine_{m}")

# Set objective
model.setObjective(
    gp.quicksum(Prices[p] * BatchesProduced[p] for p in range(NumParts)) 
    - StandardCost 
    - gp.quicksum(OvertimeHoursUsed[m] * OvertimeCost for m in range(NumMachines)), 
    gp.GRB.MAXIMIZE
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
