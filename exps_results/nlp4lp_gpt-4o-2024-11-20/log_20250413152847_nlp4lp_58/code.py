import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/58/data.json", "r") as f:
    data = json.load(f)

M = data["M"] # scalar parameter
P = data["P"] # scalar parameter
TimeRequired = np.array(data["TimeRequired"]) # ['M', 'P']
MachineCosts = np.array(data["MachineCosts"]) # ['M']
Availability = np.array(data["Availability"]) # ['M']
Prices = np.array(data["Prices"]) # ['P']
MinBatches = np.array(data["MinBatches"]) # ['P']
StandardCost = data["StandardCost"] # scalar parameter
OvertimeCost = data["OvertimeCost"] # scalar parameter
OvertimeHour = data["OvertimeHour"] # scalar parameter
MinProfit = data["MinProfit"] # scalar parameter
BatchesProduced = model.addVars(M, P, vtype=gp.GRB.INTEGER, name="BatchesProduced")
OvertimeUsed = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="OvertimeUsed")
Profit = model.addVar(vtype=gp.GRB.CONTINUOUS, name="Profit")

# Add production time constraints for each machine
for m in range(M):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[m, p] for p in range(P)) <= Availability[m],
        name=f"machine_availability_{m}"
    )

# Add overtime constraints for each machine
for m in range(M):
    # Constraint 1: Total production time minus availability cannot exceed overtime used
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[m, p] for p in range(P)) - Availability[m] <= OvertimeUsed[m],
        name=f"overtime_usage_{m}"
    )
    # Constraint 2: Overtime used cannot exceed maximum allowed overtime hours
    model.addConstr(
        OvertimeUsed[m] <= OvertimeHour,
        name=f"max_overtime_{m}"
    )

# Add constraints to ensure the minimum number of batches to be produced for each part
for p in range(P):
    model.addConstr(sum(BatchesProduced[m, p] for m in range(M)) >= MinBatches[p], name=f"min_batches_part_{p}")

# Add profit constraint
profit_expr = gp.quicksum(Prices[p] * gp.quicksum(BatchesProduced[m, p] for m in range(M)) for p in range(P)) - (
    StandardCost * gp.quicksum(Availability[m] for m in range(M)) + 
    OvertimeCost * gp.quicksum(OvertimeUsed[m] for m in range(M))
)
model.addConstr(profit_expr >= MinProfit, name="profit_constraint")

# Add non-negativity constraints for all produced batches
for m in range(M):
    for p in range(P):
        model.addConstr(BatchesProduced[m, p] >= 0, name=f"non_negativity_m{m}_p{p}")

# Add non-negativity constraints for total time used on each machine
for m in range(M):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[m, p] for p in range(P)) >= 0,
        name=f"non_neg_time_machine_{m}"
    )

# Overtime usage constraints
for m in range(M):
    model.addConstr(OvertimeUsed[m] >= 0, name=f"overtime_non_negative_{m}")
    model.addConstr(OvertimeUsed[m] <= OvertimeHour, name=f"overtime_limit_{m}")

# Add non-negativity constraints for BatchesProduced
for m in range(M):
    for p in range(P):
        model.addConstr(BatchesProduced[m, p] >= 0, name=f"non_negativity_BatchesProduced_{m}_{p}")

# Add constraints to calculate OvertimeUsed
for m in range(M):
    model.addConstr(
        OvertimeUsed[m] >= gp.quicksum(TimeRequired[m, p] * BatchesProduced[m, p] for p in range(P)) - Availability[m],
        name=f"OvertimeUsed_calc_{m}"
    )
    model.addConstr(
        OvertimeUsed[m] >= 0,
        name=f"OvertimeUsed_nonneg_{m}"
    )

# Add production time constraints for each machine
for m in range(M):
    model.addConstr(
        gp.quicksum(TimeRequired[m, p] * BatchesProduced[m, p] for p in range(P)) <= Availability[m] + OvertimeUsed[m],
        name=f"production_time_constraint_m{m}"
    )

# Add constraints to ensure overtime hours used on each machine does not exceed the maximum overtime hours available
for m in range(M):
    model.addConstr(OvertimeUsed[m] <= OvertimeHour, name=f"overtime_limit_{m}")

# Add constraints to ensure the total batches produced for each part satisfies the minimum required batch threshold
for p in range(P):
    model.addConstr(
        gp.quicksum(BatchesProduced[m, p] for m in range(M)) >= MinBatches[p],
        name=f"min_batches_part_{p}"
    )

# Add constraint to ensure total profit meets or exceeds the minimum profit requirement
model.addConstr(Profit >= MinProfit, name="min_profit_constraint")

# Set objective
model.setObjective(
    gp.quicksum(
        Prices[p] * gp.quicksum(BatchesProduced[m, p] for m in range(M)) 
        for p in range(P)
    ) 
    - StandardCost * gp.quicksum(
        TimeRequired[m, p] * BatchesProduced[m, p] 
        for m in range(M) 
        for p in range(P)
    ) 
    - OvertimeCost * gp.quicksum(OvertimeUsed[m] for m in range(M)), 
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
