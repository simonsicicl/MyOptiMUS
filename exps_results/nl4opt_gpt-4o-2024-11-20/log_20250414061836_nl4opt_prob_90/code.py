import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_90/data.json", "r") as f:
    data = json.load(f)

FullTimeShiftHours = data["FullTimeShiftHours"] # scalar parameter
PartTimeShiftHours = data["PartTimeShiftHours"] # scalar parameter
FullTimeShiftPay = data["FullTimeShiftPay"] # scalar parameter
PartTimeShiftPay = data["PartTimeShiftPay"] # scalar parameter
TotalLaborHours = data["TotalLaborHours"] # scalar parameter
TotalBudget = data["TotalBudget"] # scalar parameter
FullTimeWorkers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FullTimeWorkers")
PartTimeWorkers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PartTimeWorkers")

# Non-negativity constraint for FullTimeWorkers
model.addConstr(FullTimeWorkers >= 0, name="non_negative_full_time_workers")

# No additional code needed since the variable "PartTimeWorkers" is already defined with non-negativity by default in Gurobi (continuous variables have a non-negative domain by default).

# Add constraint to ensure total labor hours are met
model.addConstr(
    TotalLaborHours <= (FullTimeWorkers * FullTimeShiftHours) + (PartTimeWorkers * PartTimeShiftHours),
    name="labor_hours_constraint"
)

# Add total pay constraint to ensure it does not exceed TotalBudget
model.addConstr(
    FullTimeWorkers * FullTimeShiftPay + PartTimeWorkers * PartTimeShiftPay <= TotalBudget,
    name="budget_constraint"
)

# Add labor hours constraint for full-time and part-time workers
model.addConstr(
    FullTimeShiftHours * FullTimeWorkers + PartTimeShiftHours * PartTimeWorkers >= TotalLaborHours,
    name="labor_hours_constraint"
)

# Add labor cost budget constraint
model.addConstr(
    FullTimeShiftPay * FullTimeWorkers + PartTimeShiftPay * PartTimeWorkers <= TotalBudget,
    name="labor_cost_budget"
)

# Set objective
model.setObjective(FullTimeWorkers + PartTimeWorkers, gp.GRB.MINIMIZE)

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
