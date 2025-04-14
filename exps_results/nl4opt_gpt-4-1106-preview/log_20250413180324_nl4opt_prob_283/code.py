import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_283/data.json", "r") as f:
    data = json.load(f)

PartTimeHours = data["PartTimeHours"] # scalar parameter
PartTimePayment = data["PartTimePayment"] # scalar parameter
FullTimeHours = data["FullTimeHours"] # scalar parameter
FullTimePayment = data["FullTimePayment"] # scalar parameter
TotalLaborHours = data["TotalLaborHours"] # scalar parameter
TotalBudget = data["TotalBudget"] # scalar parameter
FullTimeStaff = model.addVar(vtype=gp.GRB.INTEGER, name="FullTimeStaff")
PartTimeStaff = model.addVar(vtype=gp.GRB.INTEGER, name="PartTimeStaff")

model.addConstr(FullTimeStaff >= 0, name="non_negativity_full_time_staff")

# Add constraint to ensure the number of part-time staff is non-negative
model.addConstr(PartTimeStaff >= 0, name="non_negativity_part_time_staff")

# Constraint: Total hours worked by part-time and full-time staff must equal the total labor hours required
model.addConstr(PartTimeStaff * PartTimeHours + FullTimeStaff * FullTimeHours == TotalLaborHours, "total_labor_hours")

# Add constraint for total payment to part-time and full-time staff not exceeding the TotalBudget
model.addConstr(FullTimePayment * FullTimeStaff + PartTimePayment * PartTimeStaff <= TotalBudget, name="budget_constraint")

# Define the total labor hours constraint
model.addConstr(FullTimeHours * FullTimeStaff + PartTimeHours * PartTimeStaff >= TotalLaborHours, "total_labor_hours")

# Define the total payment to all staff constraint
model.addConstr(FullTimePayment * FullTimeStaff + PartTimePayment * PartTimeStaff <= TotalBudget, name="total_payment_constraint")

# Set objective
model.setObjective(FullTimeStaff + PartTimeStaff, gp.GRB.MINIMIZE)

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
