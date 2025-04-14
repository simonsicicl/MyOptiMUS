import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/steel3/data.json", "r") as f:
    data = json.load(f)

ProductNum = data["ProductNum"] # scalar parameter
ProductionRate = np.array(data["ProductionRate"]) # ['ProductNum']
ProfitPerTon = np.array(data["ProfitPerTon"]) # ['ProductNum']
MinimumSale = np.array(data["MinimumSale"]) # ['ProductNum']
MaximumSale = np.array(data["MaximumSale"]) # ['ProductNum']
AvailableHours = data["AvailableHours"] # scalar parameter
ProductionQuantity = model.addVars(ProductNum, vtype=gp.GRB.CONTINUOUS, name="ProductionQuantity")
ProductionTime = model.addVars(ProductNum, vtype=gp.GRB.CONTINUOUS, name="ProductionTime")

# Production quantity must be non-negative  
for p in range(ProductNum):  
    model.addConstr(ProductionQuantity[p] >= 0, name=f"non_negativity_p{p}")

# Add total production hours constraint
model.addConstr(gp.quicksum(ProductionTime[i] for i in range(ProductNum)) <= AvailableHours, 
                name="total_production_hours")

# Add minimum sale constraints for each product p
for p in range(ProductNum):
    model.addConstr(ProductionQuantity[p] >= MinimumSale[p], name=f"min_sale_product_{p}")

# Add constraints to ensure production quantities do not exceed maximum allowable sales
for p in range(ProductNum):
    model.addConstr(ProductionQuantity[p] <= MaximumSale[p], name=f"max_sale_constraint_p{p}")

# Add constraints to ensure ProductionQuantity is related to ProductionTime and ProductionRate
for i in range(ProductNum):
    model.addConstr(ProductionQuantity[i] == ProductionTime[i] * ProductionRate[i], name=f"Production_constraint[{i}]")

# Add production time constraint
model.addConstr(
    gp.quicksum(ProductionQuantity[i] / ProductionRate[i] for i in range(ProductNum)) <= AvailableHours,
    name="production_time_constraint"
)

# Add minimum and maximum sale constraints
for i in range(ProductNum):
    model.addConstr(MinimumSale[i] <= ProductionQuantity[i], name=f"min_sale_{i}")
    model.addConstr(ProductionQuantity[i] <= MaximumSale[i], name=f"max_sale_{i}")

# Set objective
model.setObjective(gp.quicksum(ProfitPerTon[i] * ProductionQuantity[i] for i in range(ProductNum)), gp.GRB.MAXIMIZE)

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
