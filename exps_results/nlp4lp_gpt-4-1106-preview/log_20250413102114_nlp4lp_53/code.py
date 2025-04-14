import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/53/data.json", "r") as f:
    data = json.load(f)

M = data["M"] # scalar parameter
P = data["P"] # scalar parameter
TimeRequired = np.array(data["TimeRequired"]) # ['M', 'P']
MachineCosts = np.array(data["MachineCosts"]) # ['M']
Availability = np.array(data["Availability"]) # ['M']
Prices = np.array(data["Prices"]) # ['P']
MinBatches = np.array(data["MinBatches"]) # ['P']
ExtraCosts = np.array(data["ExtraCosts"]) # ['M']
MaxExtra = np.array(data["MaxExtra"]) # ['M']
BatchesOfPart = model.addVars(P, vtype=gp.GRB.INTEGER, name="BatchesOfPart")
TotalProductionTime = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="TotalProductionTime")
ExtraHours = model.addVars(M, vtype=gp.GRB.CONTINUOUS, name="ExtraHours")

P = data["P"] # scalar parameter
BatchesOfPart = model.addVars(P, vtype=gp.GRB.INTEGER, name="BatchesOfPart")

# All batches of each part must be non-negative
for p in range(P):
    model.addConstr(BatchesOfPart[p] >= 0, name=f"nonnegativity_part_{p}")

# Add production time constraints for each machine
for m in range(M):
    model.addConstr(gp.quicksum(BatchesOfPart[p] * TimeRequired[m, p] for p in range(P)) <= Availability[m] * M, name=f"prod_time_machine_{m}")

# Ensure each part's production in batches meets or exceeds the minimum required
for p in range(P):
    model.addConstr(BatchesOfPart[p] >= MinBatches[p], name=f"min_batches_part_{p}")

# Total machine costs and extra costs should not exceed sum of selling prices minus production costs
total_costs_constr = gp.quicksum(MachineCosts[m] + ExtraCosts[m] for m in range(M))
revenue_constr = gp.quicksum(Prices[p] * BatchesOfPart[p] for p in range(P))
production_cost_constr = gp.quicksum(TimeRequired[m, p] * BatchesOfPart[p] * MachineCosts[m] for m in range(M) for p in range(P))

model.addConstr(total_costs_constr <= revenue_constr - production_cost_constr, "Total_Costs_Limit")

# Extra hours used on each machine constraint
for m in range(M):
    model.addConstr(
        gp.quicksum(BatchesOfPart[p] * TimeRequired[m, p] for p in range(P)) -
        Availability[m] <= MaxExtra[m],
        name=f"MaxExtraHours_Machine_{m}"
    )

# Constraint: Total production time on machine m must be less than or equal to machine availability plus extra hours
# without exceeding the maximum extra hours
for m in range(M):
    model.addConstr(TotalProductionTime[m] <= Availability[m] + ExtraHours[m], name="TotalProdTime_Less_AvailPlusExtra_{}".format(m))
    model.addConstr(ExtraHours[m] <= MaxExtra[m], name="ExtraHours_Less_MaxExtra_{}".format(m))

# Total production time for each machine is the sum of time required to produce all batches of parts on that machine
for m in range(M):
    model.addConstr(TotalProductionTime[m] == gp.quicksum(TimeRequired[m, p] * BatchesOfPart[p] for p in range(P)), name=f"TotalProductionTime_machine_{m}")

# Set objective
model.setObjective(gp.quicksum(Prices[p] * BatchesOfPart[p] for p in range(P)) -
                   gp.quicksum((MachineCosts[m] * TotalProductionTime[m] +
                                ExtraCosts[m] * ExtraHours[m]) for m in range(M)),
                   gp.GRB.MAXIMIZE)

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
