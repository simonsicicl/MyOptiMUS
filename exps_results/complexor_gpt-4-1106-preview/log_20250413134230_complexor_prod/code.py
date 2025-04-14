import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/complexor/prod/data.json", "r") as f:
    data = json.load(f)

ElementNum = data["ElementNum"] # scalar parameter
CoefficientA = np.array(data["CoefficientA"]) # ['ElementNum']
ProfitCoefficientC = np.array(data["ProfitCoefficientC"]) # ['ElementNum']
UpperBoundU = np.array(data["UpperBoundU"]) # ['ElementNum']
GlobalParameterB = data["GlobalParameterB"] # scalar parameter
DecisionVariableX = model.addVars(ElementNum, vtype=gp.GRB.CONTINUOUS, name="DecisionVariableX")

inverse_sum_expr = gp.quicksum(DecisionVariableX[j] / CoefficientA[j] for j in range(ElementNum))
model.addConstr(inverse_sum_expr <= GlobalParameterB, name="inverse_coefficient_sum_constraint")

# Add non-negativity constraints for DecisionVariableX
for j in range(ElementNum):
    model.addConstr(DecisionVariableX[j] >= 0, name=f"non_negativity_{j}")

# Constraint: Each decision variable must not exceed its respective upper bound
for j in range(ElementNum):
    model.addConstr(DecisionVariableX[j] <= UpperBoundU[j], name=f"UB_constraint_{j}")

DecisionVariableX = model.addVars(range(ElementNum), vtype=gp.GRB.CONTINUOUS, name="DecisionVariableX");
model.setObjective(gp.quicksum(ProfitCoefficientC[j] * DecisionVariableX[j] for j in range(ElementNum)), gp.GRB.MAXIMIZE)

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
