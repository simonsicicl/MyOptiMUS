import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/transp/data.json", "r") as f:
    data = json.load(f)

NumberOfOrigins = data["NumberOfOrigins"] # scalar parameter
NumberOfDestinations = data["NumberOfDestinations"] # scalar parameter
SupplyOfOrigin = np.array(data["SupplyOfOrigin"]) # ['NumberOfOrigins']
DemandOfDestination = np.array(data["DemandOfDestination"]) # ['NumberOfDestinations']
CostPerUnit = np.array(data["CostPerUnit"]) # ['NumberOfOrigins', 'NumberOfDestinations']
UnitsTransported = model.addVars(NumberOfOrigins, NumberOfDestinations, vtype=gp.GRB.CONTINUOUS, name="UnitsTransported")

# Add constraints ensuring total supply from each origin matches SupplyOfOrigin
for i in range(NumberOfOrigins):
    model.addConstr(gp.quicksum(UnitsTransported[i, j] for j in range(NumberOfDestinations)) == SupplyOfOrigin[i], name=f"supply_constraint_origin_{i}")

# Add constraints to ensure the total demand at each destination is exactly satisfied
for j in range(NumberOfDestinations):
    model.addConstr(
        sum(UnitsTransported[i, j] for i in range(NumberOfOrigins)) == DemandOfDestination[j],
        name=f"demand_satisfaction_destination_{j}"
    )

# No explicit constraints are needed because the non-negativity is inherently defined by the variable bounds when creating the variables in gurobi (vtype=gp.GRB.CONTINUOUS). UnitsTransported is already non-negative.

# Add supply constraints for each origin
for i in range(NumberOfOrigins):
    model.addConstr(
        gp.quicksum(UnitsTransported[i, j] for j in range(NumberOfDestinations)) <= SupplyOfOrigin[i], 
        name=f"supply_constraint_origin_{i}"
    )

# Add constraints to ensure the total units received at each destination meet their demand
for j in range(NumberOfDestinations):
    model.addConstr(
        gp.quicksum(UnitsTransported[i, j] for i in range(NumberOfOrigins)) == DemandOfDestination[j],
        name=f"demand_constraint_dest_{j}"
    )

# The variable UnitsTransported was already defined as a non-negative continuous variable.  
# Hence, no additional constraints are needed to enforce the non-negativity.

# Set objective
model.setObjective(gp.quicksum(CostPerUnit[i, j] * UnitsTransported[i, j] for i in range(NumberOfOrigins) for j in range(NumberOfDestinations)), gp.GRB.MINIMIZE)

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
