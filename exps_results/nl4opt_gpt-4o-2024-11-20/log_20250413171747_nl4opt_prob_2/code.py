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
SeniorAccountants = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SeniorAccountants")
JuniorAccountants = model.addVar(vtype=gp.GRB.CONTINUOUS, name="JuniorAccountants")

# No additional code needed since the integrality of the SeniorAccountants variable was not mentioned and is already set as non-negative through its definition as a continuous variable.

# The variable JuniorAccountants should be a non-negative integer, not continuous. Updating its type.
JuniorAccountants.vtype = gp.GRB.INTEGER
JuniorAccountants.LB = 0

# Add constraint ensuring the total number of accountants employed meets the minimum requirement
model.addConstr(SeniorAccountants + JuniorAccountants >= MinAccountants, name="min_accountants_constraint")

# Add constraint ensuring the number of senior accountants meets or exceeds the minimum requirement
model.addConstr(SeniorAccountants >= MinSenior, name="min_senior_accountants_constraint")

# Add constraint to ensure the number of senior accountants is greater than or equal to the ratio of senior to junior accountants multiplied by the number of junior accountants
model.addConstr(SeniorAccountants >= RatioSeniorJunior * JuniorAccountants, name="senior_to_junior_ratio")

# Add wage bill constraint
model.addConstr(
    SeniorAccountants * WageSenior + JuniorAccountants * WageJunior <= MaxWageBill,
    name="wage_bill_constraint"
)

# Add constraint ensuring total number of accountants meets the minimum threshold
model.addConstr(SeniorAccountants + JuniorAccountants >= MinAccountants, name="min_accountants_constraint")

# Add constraint for the minimum requirement of senior accountants
model.addConstr(SeniorAccountants >= MinSenior, name="min_senior_accountants")

# Add constraint to ensure the ratio of senior accountants to junior accountants is respected
model.addConstr(SeniorAccountants >= RatioSeniorJunior * JuniorAccountants, name="senior_to_junior_ratio")

# Add total weekly wage bill constraint
model.addConstr(
    SeniorAccountants * WageSenior + JuniorAccountants * WageJunior <= MaxWageBill,
    name="weekly_wage_bill_constraint"
)

# Add constraint to ensure the total number of accountants meets the minimum required
model.addConstr(SeniorAccountants + JuniorAccountants >= MinAccountants, name="min_accountants_constraint")

# Ensure the number of senior accountants meets the minimum requirement
model.addConstr(SeniorAccountants >= MinSenior, name="min_senior_accountants")

# Add constraint for the minimum required ratio of senior to junior accountants
model.addConstr(SeniorAccountants >= RatioSeniorJunior * JuniorAccountants, name="ratio_senior_junior")

# Add constraint to ensure total weekly wage bill does not exceed maximum allowed
model.addConstr(SeniorAccountants * WageSenior + JuniorAccountants * WageJunior <= MaxWageBill, name="wage_bill_limit")

# Set objective
model.setObjective(SeniorAccountants * WageSenior + JuniorAccountants * WageJunior, gp.GRB.MINIMIZE)

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
