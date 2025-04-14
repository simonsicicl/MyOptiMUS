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
NumberOfRetailStores = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfRetailStores")
NumberOfFactoryOutlets = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfFactoryOutlets")

# The number of retail stores must be non-negative
# This is inherently enforced by the variable type being INTEGER
# No additional constraint is needed

# Since NumberOfFactoryOutlets is already defined as an integer variable, we just need to add a constraint to ensure it is non-negative
model.addConstr(NumberOfFactoryOutlets >= 0, name="non_negative_factory_outlets")

# Define the constraint for minimum total number of customers from retail stores and factory outlets
model.addConstr(NumberOfRetailStores * RetailCustomers + NumberOfFactoryOutlets * OutletCustomers >= MinCustomers, name="Min_Customers_Constraint")

# Total number of employees constraint
model.addConstr(NumberOfRetailStores * RetailEmployees + NumberOfFactoryOutlets * OutletEmployees <= TotalEmployees, name="total_employee_constraint")

# Add constraint for total employees required by retail stores
model.addConstr(NumberOfRetailStores * RetailEmployees <= TotalEmployees, name="total_employees_constraint")

NumberOfFactoryOutlets = model.addVar(vtype=gp.GRB.INTEGER, name='NumberOfFactoryOutlets')

# Ensure the number of customers served daily meets or exceeds the minimum required
model.addConstr(
    RetailCustomers * NumberOfRetailStores + OutletCustomers * NumberOfFactoryOutlets >= MinCustomers,
    name="min_customers_served"
)

# Ensure the number of employees used does not exceed the total number of employees available
model.addConstr(RetailEmployees * NumberOfRetailStores + OutletEmployees * NumberOfFactoryOutlets <= TotalEmployees, name="employee_limit")

# Set objective
model.setObjective(NumberOfRetailStores + NumberOfFactoryOutlets, gp.GRB.MINIMIZE)

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
