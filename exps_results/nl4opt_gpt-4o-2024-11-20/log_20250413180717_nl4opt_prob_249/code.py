import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_249/data.json", "r") as f:
    data = json.load(f)

RetailCustomers = data["RetailCustomers"] # scalar parameter
OutletCustomers = data["OutletCustomers"] # scalar parameter
RetailEmployees = data["RetailEmployees"] # scalar parameter
OutletEmployees = data["OutletEmployees"] # scalar parameter
MinCustomers = data["MinCustomers"] # scalar parameter
TotalEmployees = data["TotalEmployees"] # scalar parameter
RetailStoreCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RetailStoreCount")
OutletCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OutletCount")

# Add customer satisfaction and employee availability constraints
model.addConstr(RetailStoreCount * RetailCustomers + OutletCount * OutletCustomers >= MinCustomers, name="customer_satisfaction")
model.addConstr(RetailStoreCount * RetailEmployees + OutletCount * OutletEmployees <= TotalEmployees, name="employee_availability")

# The non-negativity constraint is implicitly satisfied as Gurobi variables are non-negative by default unless otherwise specified (e.g., with lower bounds of negative values).

# Add customer count constraint
model.addConstr(
    RetailStoreCount * RetailCustomers + OutletCount * OutletCustomers >= MinCustomers,
    name="customer_count_constraint"
)

# Add total employee constraint for stores and outlets
model.addConstr(
    RetailEmployees * RetailStoreCount + OutletEmployees * OutletCount <= TotalEmployees,
    name="employee_capacity"
)

# Change RetailStoreCount to integer (as store count must be an integer)
RetailStoreCount.vtype = gp.GRB.INTEGER

# Add employee allocation constraint 
model.addConstr(RetailStoreCount * RetailEmployees <= TotalEmployees, name="employee_allocation")

# Update OutletCount to integer, as the number of outlets in operation must be an integer count
OutletCount.vtype = gp.GRB.INTEGER

# Constraint to calculate TotalEmployeesUsedByOutlets
TotalEmployeesUsedByOutlets = OutletCount * OutletEmployees

# Non-negativity constraint for RetailStoreCount
model.addConstr(RetailStoreCount >= 0, name="non_negativity_RetailStoreCount")

# The non-negativity constraint for "OutletCount" is already enforced by defining it as a continuous variable, which is non-negative by default in Gurobi.

# Add constraint to ensure total customers served meets the minimum required number
model.addConstr(RetailCustomers * RetailStoreCount + OutletCustomers * OutletCount >= MinCustomers, name="min_customers_served")

# Add employee limit constraint
model.addConstr(
    RetailEmployees * RetailStoreCount + OutletEmployees * OutletCount <= TotalEmployees,
    name="employee_limit"
)

# Set objective
model.setObjective(RetailStoreCount + OutletCount, gp.GRB.MINIMIZE)

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
