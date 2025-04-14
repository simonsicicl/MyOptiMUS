import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_221/data.json", "r") as f:
    data = json.load(f)

PersonalLicenseCost = data["PersonalLicenseCost"] # scalar parameter
CommercialLicenseCost = data["CommercialLicenseCost"] # scalar parameter
MaxLicenses = data["MaxLicenses"] # scalar parameter
PersonalLicenseProfit = data["PersonalLicenseProfit"] # scalar parameter
CommercialLicenseProfit = data["CommercialLicenseProfit"] # scalar parameter
TotalCostLimit = data["TotalCostLimit"] # scalar parameter
NumberPersonalLicenses = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberPersonalLicenses")
NumberCommercialLicenses = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberCommercialLicenses")

# No additional code needed since the variable "NumberPersonalLicenses" is defined with non-negativity by default in Gurobi (continuous variables have a non-negative domain by default).

# The variable "NumberCommercialLicenses" is already non-negative due to its default lower bound (0) in Gurobi.

# Add constraint for maximum number of licenses
model.addConstr(NumberPersonalLicenses + NumberCommercialLicenses <= MaxLicenses, name="max_licenses_constraint")

# Add total cost constraint
model.addConstr(NumberPersonalLicenses * PersonalLicenseCost + NumberCommercialLicenses * CommercialLicenseCost <= TotalCostLimit, name="total_cost_limit")

# Add total cost constraint
model.addConstr(
    PersonalLicenseCost * NumberPersonalLicenses + CommercialLicenseCost * NumberCommercialLicenses <= TotalCostLimit,
    name="total_cost_constraint"
)

# Add constraint to ensure the total number of licenses sold does not exceed the monthly limit
model.addConstr(NumberPersonalLicenses + NumberCommercialLicenses <= MaxLicenses, name="license_limit")

# Add non-negativity constraints for NumberPersonalLicenses and NumberCommercialLicenses
model.addConstr(NumberPersonalLicenses >= 0, name="NonNegativity_NumberPersonalLicenses")
model.addConstr(NumberCommercialLicenses >= 0, name="NonNegativity_NumberCommercialLicenses")

# Set objective
model.setObjective(PersonalLicenseProfit * NumberPersonalLicenses + CommercialLicenseProfit * NumberCommercialLicenses, gp.GRB.MAXIMIZE)

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
