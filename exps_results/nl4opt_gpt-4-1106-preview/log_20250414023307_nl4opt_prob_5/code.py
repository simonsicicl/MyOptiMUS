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
TelecomInvestment = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TelecomInvestment")
HealthcareInvestment = model.addVar(vtype=gp.GRB.CONTINUOUS, name="HealthcareInvestment")

# Add non-negativity constraint for TelecomInvestment
model.addConstr(TelecomInvestment >= 0, name="non_negativity_telecom")

# Healthcare investment must be non-negative constraint
model.addConstr(HealthcareInvestment >= 0, name="healthcare_investment_nonnegativity")

# Total investment in telecom and healthcare industry does not exceed the available total investment
model.addConstr(TelecomInvestment + HealthcareInvestment <= TotalInvestment, name="total_investment_constraint")

# Add investment ratio constraint
model.addConstr(TelecomInvestment >= MinTelecomRatio * HealthcareInvestment, name="investment_ratio")

# Ensure investment in telecom does not exceed the maximum limit
model.addConstr(TelecomInvestment <= MaxTelecomInvestment, name="Max_Telecom_Investment")

# The sum of investments in telecom and healthcare must not exceed the total investment
model.addConstr(TelecomInvestment + HealthcareInvestment <= TotalInvestment, "investment_limit")

# Add constraint: The investment in telecom must not exceed the maximum amount allowed for telecom
model.addConstr(TelecomInvestment <= MaxTelecomInvestment, name="telecom_investment_limit")

model.addConstr(TelecomInvestment >= MinTelecomRatio * HealthcareInvestment, name="investment_ratio")

# Set objective
model.setObjective(TelecomInvestment * ProfitTelecom + HealthcareInvestment * ProfitHealthcare, gp.GRB.MAXIMIZE)

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
