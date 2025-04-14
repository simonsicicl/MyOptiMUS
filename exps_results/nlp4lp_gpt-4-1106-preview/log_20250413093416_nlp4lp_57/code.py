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
BatchesProduced = model.addVars(NumParts, vtype=gp.GRB.INTEGER, name="BatchesProduced")
TotalTimeUsed = model.addVars(NumMachines, NumParts, vtype=gp.GRB.CONTINUOUS, name="TotalTimeUsed")
RegularTimeUsed = model.addVars(NumMachines, vtype=gp.GRB.CONTINUOUS, name="RegularTimeUsed")
OvertimeUsed = model.addVars(NumMachines, vtype=gp.GRB.CONTINUOUS, name="OvertimeUsed")

# Add machine time availability constraints for each machine m
for m in range(NumMachines):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(NumParts)) <= Availability[m],
        name=f"machine_time_availability_{m}"
    )

# Add machine availability constraints
for m in range(NumMachines):
    model.addConstr(gp.quicksum(TimeRequired[m, p] * BatchesProduced[p] for p in range(NumParts)) <= Availability[m], name=f"machine_availability_{m}")

# At least MinBatches for p batches of each part p must be produced
for p in range(NumParts):
    model.addConstr(BatchesProduced[p] >= MinBatches[p], name=f"min_batches_part_{p}")

# Add constraints for operational hours including overtime for each machine
for m in range(NumMachines):
    model.addConstr(
        gp.quicksum(TimeRequired[m][p] * BatchesProduced[p] for p in range(NumParts)) 
        <= Availability[m] + OvertimeHour[m], 
        name="operational_hours_machine_{}".format(m)
    )

# Add non-negativity constraints for batches produced of each part
for p in range(NumParts):
    model.addConstr(BatchesProduced[p] >= 0, name="non_negative_batches_p{}".format(p))

# Add constraints for total time used on machines for producing parts
for m in range(NumMachines):
    model.addConstr(gp.quicksum(TimeRequired[m, p] * BatchesProduced[p]
                    for p in range(NumParts)) == RegularTimeUsed[m] + OvertimeUsed[m],
                    name=f"TotalTimeUsed_Machine{m}")

# Add constraints for regular time used on each machine
for m in range(NumMachines):
    model.addConstr(RegularTimeUsed[m] <= Availability[m], name=f"regular_time_avail_machine_{m}")

# Add constraints to ensure overtime used does not exceed the available hours for each machine
for m in range(NumMachines):
    model.addConstr(OvertimeUsed[m] <= OvertimeHour[m], name=f"overtime_limit_machine_{m}")

# Set objective function
model.setObjective(
    gp.quicksum(Prices[p] * BatchesProduced[p] for p in range(NumParts)) -
    StandardCost -
    gp.quicksum(MachineCosts[m] + OvertimeCost * OvertimeUsed[m] for m in range(NumMachines)),
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
