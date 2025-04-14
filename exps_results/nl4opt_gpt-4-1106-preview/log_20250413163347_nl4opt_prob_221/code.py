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
PersonalLicensesProduced = model.addVar(vtype=gp.GRB.INTEGER, name="PersonalLicensesProduced")
CommercialLicensesProduced = model.addVar(vtype=gp.GRB.INTEGER, name="CommercialLicensesProduced")

# Add constraint for non-negativity of personal licenses produced
model.addConstr(PersonalLicensesProduced >= 0, name="non_negative_personal_licenses")

# Since the variable is defined as an INTEGER, it is implicitly non-negative. 
# No further constraints are needed.

# Combined number of personal and commercial licenses produced constraint
model.addConstr(PersonalLicensesProduced + CommercialLicensesProduced <= MaxLicenses, "MaxLicensesConstraint")

# Add constraint for total cost of producing licenses
model.addConstr(PersonalLicensesProduced * PersonalLicenseCost + CommercialLicensesProduced * CommercialLicenseCost <= TotalCostLimit, "TotalCostConstraint")

# Constraint: The total number of licenses sold per month cannot exceed the maximum limit
model.addConstr(PersonalLicensesProduced + CommercialLicensesProduced <= MaxLicenses, name="max_licenses_constraint")

# Add constraint for total cost of producing licenses not to exceed the total cost limit
model.addConstr((PersonalLicenseCost * PersonalLicensesProduced) + (CommercialLicenseCost * CommercialLicensesProduced) <= TotalCostLimit, name="TotalCostConstraint")

# Define the objective function
model.setObjective((PersonalLicenseProfit * PersonalLicensesProduced) + 
                   (CommercialLicenseProfit * CommercialLicensesProduced), gp.GRB.MAXIMIZE)

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
