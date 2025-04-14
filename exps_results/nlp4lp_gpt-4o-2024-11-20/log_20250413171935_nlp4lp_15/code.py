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
ProducedUnits = model.addVars(P, vtype=gp.GRB.CONTINUOUS, name="ProducedUnits")
UpgradePerformed = model.addVar(vtype=gp.GRB.BINARY, name="UpgradePerformed")

# Add total initial cash requirement constraint
model.addConstr(
    gp.quicksum(ProducedUnits[i] * Cost[i] for i in range(P)) + UpgradePerformed * UpgradeCost <= Cash,
    name="initial_cash_requirement"
)

# Add constraint to ensure total production hours and upgrade hours do not exceed available hours
model.addConstr(
    gp.quicksum(ProducedUnits[i] * Hour[i] for i in range(P)) + UpgradePerformed * UpgradeHours <= AvailableHours,
    name="total_production_hours"
)

# Add total cost constraint
model.addConstr(
    gp.quicksum(Cost[i] * ProducedUnits[i] for i in range(P)) + UpgradeCost * UpgradePerformed <= Cash,
    name="total_cost_constraint"
)

# Add constraint ensuring that the cost to upgrade machinery does not exceed available cash
model.addConstr(UpgradePerformed * UpgradeCost <= Cash, name="upgrade_cost_constraint")

# Add total machine hours constraint
model.addConstr(
    gp.quicksum(ProducedUnits[i] * Hour[i] for i in range(P)) + (UpgradePerformed * UpgradeHours) <= AvailableHours,
    name="machine_hours_constraint"
)

# No additional code needed as the variable UpgradePerformed is already defined as binary

# Add total machine hours constraint
model.addConstr(
    gp.quicksum(ProducedUnits[i] * Hour[i] for i in range(P)) + UpgradePerformed * UpgradeHours <= AvailableHours,
    name="machine_hours_limit"
)

# Add cash usage constraint
model.addConstr(
    gp.quicksum(ProducedUnits[i] * Cost[i] for i in range(P)) + UpgradePerformed * UpgradeCost <= Cash,
    name="cash_limit"
)

# Set objective
model.setObjective(
    gp.quicksum(
        ProducedUnits[i] * Price[i] - 
        ProducedUnits[i] * Cost[i] - 
        ProducedUnits[i] * Price[i] * InvestPercentage[i] 
        for i in range(P)
    ) - UpgradePerformed * UpgradeCost,
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
