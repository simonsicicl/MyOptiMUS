import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/CFLP/data.json", "r") as f:
    data = json.load(f)

NumberOfFacilities = data["NumberOfFacilities"] # scalar parameter
NumberOfCustomers = data["NumberOfCustomers"] # scalar parameter
FacilityFixedCost = np.array(data["FacilityFixedCost"]) # ['NumberOfFacilities']
FacilityToCustomerTransportCost = np.array(data["FacilityToCustomerTransportCost"]) # ['NumberOfFacilities', 'NumberOfCustomers']
FacilityCapacity = np.array(data["FacilityCapacity"]) # ['NumberOfFacilities']
CustomerDemand = np.array(data["CustomerDemand"]) # ['NumberOfCustomers']
AmountTransported = model.addVars(NumberOfFacilities, NumberOfCustomers, vtype=gp.GRB.CONTINUOUS, name="AmountTransported")
FacilityLocated = model.addVars(NumberOfFacilities, vtype=gp.GRB.BINARY, name="FacilityLocated")

# Add facility capacity constraints
for i in range(NumberOfFacilities):
    model.addConstr(
        gp.quicksum(AmountTransported[i, j] for j in range(NumberOfCustomers)) <= FacilityCapacity[i],
        name=f"facility_capacity_{i}"
    )

# Add constraint to ensure the total number of facilities to be opened equals NumberOfFacilities
model.addConstr(FacilityLocated.sum() == NumberOfFacilities, name="facility_count")

# Add constraints to ensure each customer's demand is served
for j in range(NumberOfCustomers):
    model.addConstr(
        gp.quicksum(AmountTransported[i, j] for i in range(NumberOfFacilities)) == CustomerDemand[j],
        name=f"customer_demand_{j}"
    )

# Add constraints to ensure the total output for each facility does not exceed its capacity
for i in range(NumberOfFacilities):
    model.addConstr(
        gp.quicksum(AmountTransported[i, j] for j in range(NumberOfCustomers)) <= FacilityCapacity[i] * FacilityLocated[i], 
        name=f"facility_capacity_{i}"
    )

# No code needed as these are fixed scalar parameters and the constraint doesn't involve variables.

# Add constraints to ensure goods can only be transported if the facility is operational
for i in range(NumberOfFacilities):
    for j in range(NumberOfCustomers):
        model.addConstr(AmountTransported[i, j] <= FacilityCapacity[i] * FacilityLocated[i], name=f"transport_limit_{i}_{j}")

# Add capacity constraints ensuring the total goods transported from each facility do not exceed its capacity if the facility is open
for i in range(NumberOfFacilities):
    model.addConstr(
        gp.quicksum(AmountTransported[i, j] for j in range(NumberOfCustomers)) <= FacilityCapacity[i] * FacilityLocated[i],
        name=f"facility_capacity_{i}"
    )

# Add customer demand satisfaction constraints
for j in range(NumberOfCustomers):
    model.addConstr(
        gp.quicksum(AmountTransported[i, j] for i in range(NumberOfFacilities)) == CustomerDemand[j],
        name=f"customer_demand_{j}"
    )

# Non-negativity constraints for AmountTransported
for i in range(NumberOfFacilities):
    for j in range(NumberOfCustomers):
        model.addConstr(AmountTransported[i, j] >= 0, name=f"non_negativity_{i}_{j}")

# No additional code required since the variable 'FacilityLocated' is already defined as a binary variable.

# Set objective
model.setObjective(
    gp.quicksum(FacilityFixedCost[i] * FacilityLocated[i] for i in range(NumberOfFacilities)) +
    gp.quicksum(FacilityToCustomerTransportCost[i, j] * AmountTransported[i, j]
                for i in range(NumberOfFacilities) for j in range(NumberOfCustomers)),
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
