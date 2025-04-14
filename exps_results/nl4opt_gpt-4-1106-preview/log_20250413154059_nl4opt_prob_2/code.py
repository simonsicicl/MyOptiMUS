import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_2/data.json", "r") as f:
    data = json.load(f)

WageSenior = data["WageSenior"] # scalar parameter
WageJunior = data["WageJunior"] # scalar parameter
MinAccountants = data["MinAccountants"] # scalar parameter
MinSenior = data["MinSenior"] # scalar parameter
RatioSeniorJunior = data["RatioSeniorJunior"] # scalar parameter
MaxWageBill = data["MaxWageBill"] # scalar parameter
NumSeniorAccountants = model.addVar(vtype=gp.GRB.INTEGER, name="NumSeniorAccountants")
NumJuniorAccountants = model.addVar(vtype=gp.GRB.INTEGER, name="NumJuniorAccountants")

# No additional code needed because the variable NumSeniorAccountants is already defined as an integer

# The number of junior accountants must be a non-negative integer
# The code to define NumJuniorAccountants as an integer variable is already given.
# Therefore, we do not need to add any new constraints to the model for this requirement.

# Add constraint for minimum number of accountants
model.addConstr(NumSeniorAccountants + NumJuniorAccountants >= MinAccountants, name="min_accountants")

# Ensure number of senior accountants meets or exceeds the minimum requirement
model.addConstr(NumSeniorAccountants >= MinSenior, name="min_senior_accountants")

# Constraint: Number of senior accountants must be greater than or equal to the product of the ratio of senior to junior accountants and the number of junior accountants
model.addConstr(NumSeniorAccountants >= RatioSeniorJunior * NumJuniorAccountants, name="senior_to_junior_ratio")

# Wage constraint for senior and junior accountants
model.addConstr(WageSenior * NumSeniorAccountants + WageJunior * NumJuniorAccountants <= MaxWageBill, "wage_bill_constraint")

# Ensure the number of accountants meets the minimum requirement
model.addConstr(NumSeniorAccountants + NumJuniorAccountants >= MinAccountants, "min_accountants_requirement")

# Ensure the number of senior accountants meets the minimum requirement
model.addConstr(NumSeniorAccountants >= MinSenior, name="min_senior_accountants")

# Constraint to maintain the ratio of senior to junior accountants
model.addConstr(NumSeniorAccountants <= RatioSeniorJunior * NumJuniorAccountants, name="senior_to_junior_ratio")

# Ensure the weekly wage bill does not exceed the maximum allowable amount
model.addConstr(WageSenior * NumSeniorAccountants + WageJunior * NumJuniorAccountants <= MaxWageBill, "max_weekly_wage_bill")

# Set objective
model.setObjective(WageSenior * NumSeniorAccountants + WageJunior * NumJuniorAccountants, gp.GRB.MINIMIZE)

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
