import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_5/data.json", "r") as f:
    data = json.load(f)

TotalInvestment = data["TotalInvestment"] # scalar parameter
MaxTelecomInvestment = data["MaxTelecomInvestment"] # scalar parameter
MinTelecomRatio = data["MinTelecomRatio"] # scalar parameter
ProfitTelecom = data["ProfitTelecom"] # scalar parameter
ProfitHealthcare = data["ProfitHealthcare"] # scalar parameter
InvestmentTelecom = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InvestmentTelecom")
InvestmentHealthcare = model.addVar(vtype=gp.GRB.CONTINUOUS, name="InvestmentHealthcare")

# No code is needed: Gurobi variables by default have non-negativity constraints unless explicitly set otherwise.

# The investment in healthcare must be non-negative
model.addConstr(InvestmentHealthcare >= 0, name="non_negative_investment_healthcare")

# Add constraint to ensure the total investment in telecom and healthcare does not exceed the available total investment amount
model.addConstr(InvestmentTelecom + InvestmentHealthcare <= TotalInvestment, name="investment_limit")

# Investment in telecom must be at least MinTelecomRatio times the investment in healthcare
model.addConstr(InvestmentTelecom >= MinTelecomRatio * InvestmentHealthcare, name="telecom_investment_minimum")

# Add telecom investment constraint
model.addConstr(InvestmentTelecom <= MaxTelecomInvestment, name="telecom_investment_limit")

# Add constraint to ensure the total investment in both industries does not exceed the total investment budget
model.addConstr(InvestmentTelecom + InvestmentHealthcare <= TotalInvestment, name="total_investment_constraint")

# Add telecom investment constraint
model.addConstr(InvestmentTelecom <= MaxTelecomInvestment, name="telecom_investment_limit")

# Add minimum telecom investment ratio constraint
model.addConstr(InvestmentTelecom >= MinTelecomRatio * InvestmentHealthcare, name="min_telecom_investment")

# Set objective
model.setObjective(InvestmentTelecom * ProfitTelecom + InvestmentHealthcare * ProfitHealthcare, gp.GRB.MAXIMIZE)

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
