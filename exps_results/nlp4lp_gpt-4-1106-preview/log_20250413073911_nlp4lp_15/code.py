import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/15/data.json", "r") as f:
    data = json.load(f)

P = data["P"] # scalar parameter
Cash = data["Cash"] # scalar parameter
Hour = np.array(data["Hour"]) # ['P']
Cost = np.array(data["Cost"]) # ['P']
Price = np.array(data["Price"]) # ['P']
InvestPercentage = np.array(data["InvestPercentage"]) # ['P']
UpgradeHours = data["UpgradeHours"] # scalar parameter
UpgradeCost = data["UpgradeCost"] # scalar parameter
AvailableHours = data["AvailableHours"] # scalar parameter
UnitsProduced = model.addVars(P, vtype=gp.GRB.CONTINUOUS, name="UnitsProduced")
UpgradeBinary = model.addVar(vtype=gp.GRB.BINARY, name="UpgradeBinary")
Income = model.addVars(P, vtype=gp.GRB.CONTINUOUS, name="Income")
TotalNetIncome = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalNetIncome")

# Add constraint for initial cash not exceeding available cash including production and upgrade costs
production_cost = gp.quicksum(UnitsProduced[i] * Cost[i] for i in range(P))
machinery_upgrade_cost = UpgradeBinary * UpgradeCost
model.addConstr(production_cost + machinery_upgrade_cost <= Cash, "initial_cash_constraint")

# Total production hours for all products and potential upgrading should not exceed the total available machine hours
total_production_hours = gp.quicksum(UnitsProduced[p] * Hour[p] for p in range(P))
model.addConstr(total_production_hours + UpgradeBinary * UpgradeHours <= AvailableHours, name="TotalMachineHours")

# Add constraint for total production and upgrade costs not exceeding available cash
model.addConstr(gp.quicksum(Cost[i] * UnitsProduced[i] for i in range(P)) + UpgradeBinary * UpgradeCost <= Cash, name="budget_constraint")

# Add constraint for upgrade machinery cost not exceeding available cash
model.addConstr(UpgradeCost * UpgradeBinary <= Cash, name="upgrade_cost_limit")

# Add constraint: Production hours for upgrading machinery do not exceed AvailableHours
model.addConstr(
    gp.quicksum(UnitsProduced[i] * Hour[i] for i in range(P)) + 
    UpgradeBinary * UpgradeHours <= AvailableHours,
    name="ProductionHoursConstraint"
)

# Set objective
model.setObjective(
    gp.quicksum(
        UnitsProduced[i] * (Price[i] - Cost[i]) * (1 - InvestPercentage[i])
        for i in range(P)
    ) - UpgradeCost * UpgradeBinary,
    gp.GRB.MAXIMIZE
)

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
