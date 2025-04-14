import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_15/data.json", "r") as f:
    data = json.load(f)

WageSenior = data["WageSenior"] # scalar parameter
WageYoung = data["WageYoung"] # scalar parameter
MaxWageBill = data["MaxWageBill"] # scalar parameter
MinWorkers = data["MinWorkers"] # scalar parameter
MinYoung = data["MinYoung"] # scalar parameter
YoungToSeniorRatio = data["YoungToSeniorRatio"] # scalar parameter
NumberSenior = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberSenior")
NumberYoung = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberYoung")

# Add maximum wage bill constraint
model.addConstr(
    NumberSenior * WageSenior + NumberYoung * WageYoung <= MaxWageBill, 
    name="max_wage_bill"
)

# Add minimum worker constraint to ensure the daily average is at least MinWorkers
model.addConstr((NumberSenior + NumberYoung) / 7 >= MinWorkers, name="min_workers_per_day")

# Add constraint to ensure the weekly employment of young adults is sufficient to meet the daily minimum requirement for 7 days
model.addConstr(NumberYoung >= 7 * MinYoung, name="weekly_young_employment")

# Add constraint to ensure the number of young adults is at least YoungToSeniorRatio times the number of senior citizens 
model.addConstr(NumberYoung >= YoungToSeniorRatio * NumberSenior, name="young_to_senior_ratio")

# Non-negativity constraint for the number of senior citizens
model.addConstr(NumberSenior >= 0, name="non_negative_senior")

# The variable "NumberYoung" is already defined as non-negative due to its default lower bound (0) in Gurobi.
# No additional constraints are needed to enforce non-negativity.

# Changing the variable "NumberSenior" to integer type to satisfy the integrality constraint
NumberSenior.vtype = gp.GRB.INTEGER

# Changing the variable "NumberYoung" to integer type to satisfy the integrality constraint
NumberYoung.vtype = gp.GRB.INTEGER

# Add weekly wage bill constraint
model.addConstr(NumberSenior * WageSenior + NumberYoung * WageYoung <= MaxWageBill, name="weekly_wage_bill_constraint")

# Add constraint to ensure the total number of workers meets the minimum daily requirement
model.addConstr(NumberSenior + NumberYoung >= MinWorkers, name="min_workers_requirement")

# Add constraint to ensure the number of young adults meets the minimum daily requirement
model.addConstr(NumberYoung >= MinYoung, name="min_young_employment")

# Add constraint to ensure fraction of young adults meets the minimum relative to senior citizens
model.addConstr(NumberYoung >= YoungToSeniorRatio * NumberSenior, name="young_to_senior_ratio")

# Set objective
model.setObjective(WageSenior * NumberSenior + WageYoung * NumberYoung, gp.GRB.MINIMIZE)

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
