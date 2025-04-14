import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_195/data.json", "r") as f:
    data = json.load(f)

CarrierCapacity = data["CarrierCapacity"] # scalar parameter
OwlCapacity = data["OwlCapacity"] # scalar parameter
MaxOwlPercentage = data["MaxOwlPercentage"] # scalar parameter
TotalTreats = data["TotalTreats"] # scalar parameter
TreatsPerCarrier = data["TreatsPerCarrier"] # scalar parameter
TreatsPerOwl = data["TreatsPerOwl"] # scalar parameter
MinCarrierPigeons = data["MinCarrierPigeons"] # scalar parameter
CarrierPigeonsUsed = model.addVar(vtype=gp.GRB.INTEGER, name="CarrierPigeonsUsed")
OwlsUsed = model.addVar(vtype=gp.GRB.INTEGER, name="OwlsUsed")

# The non-negativity constraint for CarrierPigeonsUsed is inherent to the variable declaration (integer type)
# Therefore, no separate constraint is needed as Gurobi handles non-negativity for variables by default.

# The variable OwlsUsed should already be non-negative due to its declaration as an INTEGER
# No additional constraints are needed

# At most MaxOwlPercentage percent of the total number of birds used can be owls
model.addConstr(OwlsUsed - MaxOwlPercentage * (CarrierPigeonsUsed + OwlsUsed) <= 0, name="MaxOwlPercentageConstraint")

# Constraint: Total treats used by carrier pigeons and owls cannot exceed TotalTreats
model.addConstr(CarrierPigeonsUsed * TreatsPerCarrier + OwlsUsed * TreatsPerOwl <= TotalTreats, "TotalTreatsConstraint")

# At least a minimum number of carrier pigeons must be used constraint
model.addConstr(CarrierPigeonsUsed >= MinCarrierPigeons, name="min_carrier_pigeons")

# Treats constraint for carrier pigeons and owls
model.addConstr(TreatsPerCarrier * CarrierPigeonsUsed + TreatsPerOwl * OwlsUsed <= TotalTreats, "TreatsConstraint")

# Constraint: Number of owls used must not exceed the maximum percentage allowed of the total number of birds
model.addConstr(OwlsUsed <= MaxOwlPercentage * (CarrierPigeonsUsed + OwlsUsed), name="max_owls_percentage")

# Add constraint to ensure a minimum number of carrier pigeons are used
model.addConstr(CarrierPigeonsUsed >= MinCarrierPigeons, name="min_carrier_pigeons")

# Set objective
model.setObjective(CarrierCapacity * CarrierPigeonsUsed + OwlCapacity * OwlsUsed, gp.GRB.MAXIMIZE)

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
