import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/CapacitatedWarehouseLocation/data.json", "r") as f:
    data = json.load(f)

NumberOfLocations = data["NumberOfLocations"] # scalar parameter
NumberOfCustomers = data["NumberOfCustomers"] # scalar parameter
CustomerDemand = np.array(data["CustomerDemand"]) # ['NumberOfCustomers']
ServiceAllocationCost = np.array(data["ServiceAllocationCost"]) # ['NumberOfLocations', 'NumberOfCustomers']
WarehouseCapacity = np.array(data["WarehouseCapacity"]) # ['NumberOfLocations']
MinimumDemandFromWarehouse = np.array(data["MinimumDemandFromWarehouse"]) # ['NumberOfLocations']
MinimumOpenWarehouses = data["MinimumOpenWarehouses"] # scalar parameter
MaximumOpenWarehouses = data["MaximumOpenWarehouses"] # scalar parameter
WarehouseFixedCost = np.array(data["WarehouseFixedCost"]) # ['NumberOfLocations']
ProductsSupplied = model.addVars(NumberOfLocations, NumberOfCustomers, vtype=gp.GRB.CONTINUOUS, name="ProductsSupplied")
WarehouseOpenStatus = model.addVars(NumberOfLocations, vtype=gp.GRB.BINARY, name="WarehouseOpenStatus")

# Add constraints to ensure customer demand is met by the sum of products supplied from all warehouses
for c in range(NumberOfCustomers):
    model.addConstr(gp.quicksum(ProductsSupplied[l, c] for l in range(NumberOfLocations)) >= CustomerDemand[c], name=f"demand_met_{c}")

# Warehouse capacity constraints
for l in range(NumberOfLocations):
    model.addConstr(gp.quicksum(ProductsSupplied[l, c] for c in range(NumberOfCustomers)) <= WarehouseCapacity[l], name=f"WarehouseCapacity{l}")

# Add constraints to ensure that if a warehouse is open, it meets at least the MinimumDemandFromWarehouse
for l in range(NumberOfLocations):
    model.addConstr(gp.quicksum(ProductsSupplied[l, c] for c in range(NumberOfCustomers)) >= WarehouseOpenStatus[l] * MinimumDemandFromWarehouse[l], name=f"MinDemand_Warehouse{l}")

# Ensure that at least the minimum number of warehouses are open
model.addConstr(gp.quicksum(WarehouseOpenStatus[l] for l in range(NumberOfLocations)) >= MinimumOpenWarehouses, name="min_warehouses_open")

# Add constraint for the maximum number of operational warehouses
model.addConstr(gp.quicksum(WarehouseOpenStatus[l] for l in range(NumberOfLocations)) <= MaximumOpenWarehouses, name="MaxOperationalWarehouses")

# Since WarehouseOpenStatus is already defined as a binary variable, no additional constraints are needed

# Add warehouse capacity constraints
for l in range(NumberOfLocations):
    model.addConstr(gp.quicksum(ProductsSupplied[l, c] for c in range(NumberOfCustomers)) <= WarehouseCapacity[l] * WarehouseOpenStatus[l], name=f"warehouse_capacity_{l}")

# Ensure supply meets demand for each customer
for c in range(NumberOfCustomers):
    model.addConstr(gp.quicksum(ProductsSupplied[l, c] for l in range(NumberOfLocations)) == CustomerDemand[c], 
                    name=f"demand_constraint_{c}")

# Warehouses must supply a minimum quantity or none if not open
for l in range(NumberOfLocations):
    model.addConstr(gp.quicksum(ProductsSupplied[l, c] for c in range(NumberOfCustomers)) >= MinimumDemandFromWarehouse[l] * WarehouseOpenStatus[l], name=f"min_demand_warehouse_{l}")

# Ensure the minimum number of warehouses are open
model.addConstr(gp.quicksum(WarehouseOpenStatus[l] for l in range(NumberOfLocations)) >= MinimumOpenWarehouses, name="min_warehouses_open")

# Maximum number of warehouses open constraint
model.addConstr(gp.quicksum(WarehouseOpenStatus[l] for l in range(NumberOfLocations)) <= MaximumOpenWarehouses, name="MaxOpenWarehouses")

# Set objective function
objective = gp.quicksum(ServiceAllocationCost[l, c] * ProductsSupplied[l, c] for l in range(NumberOfLocations) for c in range(NumberOfCustomers)) \
            + gp.quicksum(WarehouseFixedCost[l] * WarehouseOpenStatus[l] for l in range(NumberOfLocations))
model.setObjective(objective, gp.GRB.MINIMIZE)

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
