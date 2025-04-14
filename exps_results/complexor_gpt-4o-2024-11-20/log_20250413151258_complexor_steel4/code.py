import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/steel4/data.json", "r") as f:
    data = json.load(f)

NumProducts = data["NumProducts"] # scalar parameter
NumStages = data["NumStages"] # scalar parameter
ProductionRate = np.array(data["ProductionRate"]) # ['NumProducts', 'NumStages']
ProfitPerTon = np.array(data["ProfitPerTon"]) # ['NumProducts']
MinCommitment = np.array(data["MinCommitment"]) # ['NumProducts']
MaxMarketLimit = np.array(data["MaxMarketLimit"]) # ['NumProducts']
StageAvailability = np.array(data["StageAvailability"]) # ['NumStages']
TonsProduced = model.addVars(NumProducts, vtype=gp.GRB.CONTINUOUS, name="TonsProduced")

# Add non-negativity constraints for TonsProduced
for p in range(NumProducts):
    model.addConstr(TonsProduced[p] >= 0, name=f"TonsProduced_nonneg_{p}")

# Add constraints to ensure total hours used in each stage by all products do not exceed stage availability
for s in range(NumStages):
    model.addConstr(
        gp.quicksum(TonsProduced[p] * ProductionRate[p, s] for p in range(NumProducts)) <= StageAvailability[s],
        name=f"StageHoursLimit_s{s}"
    )

# Add constraints to ensure each product meets its minimum production commitment
for p in range(NumProducts):
    model.addConstr(TonsProduced[p] >= MinCommitment[p], name=f"min_commitment_product_{p}")

# Add market limit constraints
for p in range(NumProducts):
    model.addConstr(TonsProduced[p] <= MaxMarketLimit[p], name=f"market_limit_{p}")

# Add market constraints  
for p in range(NumProducts):  
    model.addConstr(MinCommitment[p] <= TonsProduced[p], name=f"min_commitment_{p}")  
    model.addConstr(TonsProduced[p] <= MaxMarketLimit[p], name=f"max_market_limit_{p}")

# Add constraints for stage availability
for s in range(NumStages):
    model.addConstr(
        gp.quicksum(TonsProduced[p] / ProductionRate[p, s] for p in range(NumProducts)) <= StageAvailability[s],
        name=f"stage_availability_{s}"
    )

# Add non-negativity constraints for production variables
for p in range(NumProducts):
    model.addConstr(TonsProduced[p] >= 0, name=f"non_negativity_p{p}")

# Set objective
model.setObjective(gp.quicksum(ProfitPerTon[p] * TonsProduced[p] for p in range(NumProducts)), gp.GRB.MAXIMIZE)

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
