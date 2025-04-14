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

# Non-negative production quantity constraint for each product
for p in range(ProductNum):
    model.addConstr(ProductionQuantity[p] >= 0, name="non_negativity_constraint_p{0}".format(p))

# Add total production hours constraint
total_production_hours = gp.quicksum(ProductionQuantity[p] / ProductionRate[p] for p in range(ProductNum))
model.addConstr(total_production_hours <= AvailableHours, name="total_production_hours")

# Ensure each product is produced at least its minimum sale amount
for p in range(ProductNum):
    model.addConstr(ProductionQuantity[p] >= MinimumSale[p], name=f"min_sale_prod_{p}")

# Ensure each product is sold no more than its maximum sale limit
for p in range(ProductNum):
    model.addConstr(ProductionQuantity[p] <= MaximumSale[p], name=f"max_sales_{p}")

# Add constraint for total production time not exceeding available hours
total_production_time = gp.quicksum((ProductionQuantity[p] / ProductionRate[p]) for p in range(ProductNum))
model.addConstr(total_production_time <= AvailableHours, name="production_time_limit")

ProductionQuantity = model.addVars(ProductNum, vtype=gp.GRB.CONTINUOUS, name='ProductionQuantity')

ProductionQuantity = model.addVars(ProductNum, vtype=gp.GRB.CONTINUOUS, name='ProductionQuantity')

# Define the objective function
model.setObjective(gp.quicksum(ProfitPerTon[p] * ProductionQuantity[p] for p in range(ProductNum)), gp.GRB.MAXIMIZE)

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
