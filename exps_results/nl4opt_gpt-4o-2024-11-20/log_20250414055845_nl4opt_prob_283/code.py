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
FullTimeStaff = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FullTimeStaff")
PartTimeStaff = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PartTimeStaff")

# Non-negativity constraint for the number of full-time staff
model.addConstr(FullTimeStaff >= 0, name="nonnegative_full_time_staff")

# No code is needed; the non-negativity constraint is automatically enforced due to the default non-negative domain of continuous variables in Gurobi.

# Add labor hour balance constraint
model.addConstr(
    FullTimeStaff * FullTimeHours + PartTimeStaff * PartTimeHours == TotalLaborHours,
    name="labor_hour_balance"
)

# Add weekly payment constraint
model.addConstr(
    FullTimeStaff * FullTimePayment + PartTimeStaff * PartTimePayment <= TotalBudget,
    name="weekly_payment_constraint"
)

# Non-negativity constraint for the number of part-time staff
model.addConstr(PartTimeStaff >= 0, name="nonnegative_part_time_staff")

# Adding labor hour constraint
model.addConstr(FullTimeHours * FullTimeStaff + PartTimeHours * PartTimeStaff >= TotalLaborHours, 
                name="labor_hour_constraint")

# Add budget constraint for full-time and part-time staff
model.addConstr(
    FullTimePayment * FullTimeStaff + PartTimePayment * PartTimeStaff <= TotalBudget, 
    name="weekly_payment_budget"
)

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
