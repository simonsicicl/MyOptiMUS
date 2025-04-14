import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_92/data.json", "r") as f:
    data = json.load(f)

ToysMedium = data["ToysMedium"] # scalar parameter
OperatorsMedium = data["OperatorsMedium"] # scalar parameter
ToysSmall = data["ToysSmall"] # scalar parameter
OperatorsSmall = data["OperatorsSmall"] # scalar parameter
ToysMin = data["ToysMin"] # scalar parameter
OperatorsTotal = data["OperatorsTotal"] # scalar parameter
MediumFactories = model.addVar(vtype=gp.GRB.CONTINUOUS, name="MediumFactories")
SmallFactories = model.addVar(vtype=gp.GRB.INTEGER, name="SmallFactories")

# Adding constraints for production and operator limitations

# Constraint: Production requirements
model.addConstr(
    ToysMedium * MediumFactories + ToysSmall * SmallFactories >= ToysMin,
    name="production_constraint"
)

# Constraint: Operator availability
model.addConstr(
    OperatorsMedium * MediumFactories + OperatorsSmall * SmallFactories <= OperatorsTotal,
    name="operator_constraint"
)

# Add non-negativity constraint for SmallFactories
model.addConstr(SmallFactories >= 0, name="non_negative_small_factories")

# Add constraint to ensure daily toy production meets the minimum required amount
model.addConstr((ToysMedium * MediumFactories) + (ToysSmall * SmallFactories) >= ToysMin, name="min_daily_toy_production")

# Add constraint to ensure total operators required does not exceed availability
model.addConstr(
    MediumFactories * OperatorsMedium + SmallFactories * OperatorsSmall <= OperatorsTotal,
    name="operator_limit"
)

# Add constraint to ensure total toys produced meets or exceeds the daily minimum requirement
model.addConstr(
    MediumFactories * ToysMedium + SmallFactories * ToysSmall >= ToysMin,
    name="daily_minimum_toy_production"
)

# Add operator usage constraint
model.addConstr(
    MediumFactories * OperatorsMedium + SmallFactories * OperatorsSmall <= OperatorsTotal,
    name="operator_usage_limit"
)

# Set objective
model.setObjective(MediumFactories + SmallFactories, gp.GRB.MINIMIZE)

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
