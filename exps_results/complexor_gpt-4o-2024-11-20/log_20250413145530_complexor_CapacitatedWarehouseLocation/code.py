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
SupplyFromWarehouseToCustomer = model.addVars(NumberOfLocations, NumberOfCustomers, vtype=gp.GRB.CONTINUOUS, name="SupplyFromWarehouseToCustomer")
WarehouseOpen = model.addVars(NumberOfLocations, vtype=gp.GRB.BINARY, name="WarehouseOpen")

# Ensure each customer's demand is met through allocations from warehouses
for c in range(NumberOfCustomers):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for l in range(NumberOfLocations)) == CustomerDemand[c],
        name=f"customer_demand_{c}"
    )

# Add warehouse capacity constraints
for l in range(NumberOfLocations):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for c in range(NumberOfCustomers)) <= WarehouseCapacity[l],
        name=f"warehouse_capacity_{l}"
    )

# Add constraints to ensure that if a warehouse is operational, it meets at least MinimumDemandFromWarehouse
for l in range(NumberOfLocations):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for c in range(NumberOfCustomers)) 
        >= MinimumDemandFromWarehouse[l] * WarehouseOpen[l],
        name=f"min_demand_warehouse_{l}"
    )

# Add constraint to ensure at least MinimumOpenWarehouses warehouses are operational
model.addConstr(gp.quicksum(WarehouseOpen[l] for l in range(NumberOfLocations)) >= MinimumOpenWarehouses, name="min_warehouses_operational")

# Add constraint to ensure at most MaximumOpenWarehouses can be operational
model.addConstr(gp.quicksum(WarehouseOpen[l] for l in range(NumberOfLocations)) <= MaximumOpenWarehouses, name="max_warehouses_operational")

# Add constraints to ensure supply from any warehouse to any customer does not exceed the warehouse's capacity
for l in range(NumberOfLocations):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for c in range(NumberOfCustomers)) <= WarehouseCapacity[l], 
        name=f"warehouse_capacity_{l}"
    )

# SupplyFromWarehouseToCustomer non-negativity constraints
for l in range(NumberOfLocations):
    for c in range(NumberOfCustomers):
        model.addConstr(SupplyFromWarehouseToCustomer[l, c] >= 0, name=f"non_negative_supply_{l}_{c}")

# Add maximum supply constraints for each warehouse
for l in range(NumberOfLocations):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for c in range(NumberOfCustomers)) <= WarehouseCapacity[l] * WarehouseOpen[l],
        name=f"max_supply_warehouse_{l}"
    )

# Add total supply constraints ensuring it is 0 when a warehouse is closed
for l in range(NumberOfLocations):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for c in range(NumberOfCustomers)) 
        >= MinimumDemandFromWarehouse[l] * WarehouseOpen[l],
        name=f"total_supply_constr_location_{l}"
    )

# Add constraints to ensure a warehouse can only supply customers if it is open
for l in range(NumberOfLocations):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for c in range(NumberOfCustomers)) 
        <= WarehouseCapacity[l] * WarehouseOpen[l], 
        name=f"warehouse_supply_constraint_{l}"
    )

# Add customer demand satisfaction constraints
for c in range(NumberOfCustomers):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for l in range(NumberOfLocations)) == CustomerDemand[c],
        name=f"demand_satisfaction_customer_{c}"
    )

# Add constraint to enforce the minimum number of warehouses to be operational
model.addConstr(gp.quicksum(WarehouseOpen[l] for l in range(NumberOfLocations)) >= MinimumOpenWarehouses, name="min_warehouses_open")

# Add constraint to enforce the maximum number of operational warehouses
model.addConstr(gp.quicksum(WarehouseOpen[l] for l in range(NumberOfLocations)) <= MaximumOpenWarehouses, name="max_operational_warehouses")

# Ensure that demand from a warehouse exceeds the minimum if the warehouse is operational
for l in range(NumberOfLocations):
    model.addConstr(
        gp.quicksum(SupplyFromWarehouseToCustomer[l, c] for c in range(NumberOfCustomers)) 
        >= MinimumDemandFromWarehouse[l] * WarehouseOpen[l], 
        name=f"MinimumDemandFromWarehouse_{l}"
    )

# Set objective
model.setObjective(
    gp.quicksum(
        SupplyFromWarehouseToCustomer[l, c] * ServiceAllocationCost[l, c]
        for l in range(NumberOfLocations) for c in range(NumberOfCustomers)
    )
    + gp.quicksum(
        WarehouseOpen[l] * WarehouseFixedCost[l]
        for l in range(NumberOfLocations)
    ),
    gp.GRB.MINIMIZE
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
