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
FullTimeWorkers = model.addVar(vtype=gp.GRB.INTEGER, name="FullTimeWorkers")
PartTimeWorkers = model.addVar(vtype=gp.GRB.INTEGER, name="PartTimeWorkers")

# Full-time workers must be non-negative
model.addConstr(FullTimeWorkers >= 0, name="non_negative_full_time_workers")

# Add constraint to ensure the number of part time workers is non-negative
model.addConstr(PartTimeWorkers >= 0, name="non_negativity_part_time_workers")

# Add constraint to ensure the sum of labor hours from full-time and part-time workers meets or exceeds total required hours
model.addConstr(FullTimeWorkers * FullTimeShiftHours + PartTimeWorkers * PartTimeShiftHours >= TotalLaborHours, "labor_hours_constraint")

# Add constraint for the total payment for all workers not to exceed the TotalBudget
model.addConstr(FullTimeWorkers * FullTimeShiftPay + PartTimeWorkers * PartTimeShiftPay <= TotalBudget, name="budget_constraint")

# Add constraint for required labor hours
model.addConstr(FullTimeWorkers * FullTimeShiftHours + PartTimeWorkers * PartTimeShiftHours >= TotalLaborHours, name="labor_hours_requirement")

# Budget constraint for full time and part time workers' payment
model.addConstr(FullTimeWorkers * FullTimeShiftPay + PartTimeWorkers * PartTimeShiftPay <= TotalBudget, name="labor_budget")

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
