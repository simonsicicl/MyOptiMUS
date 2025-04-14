import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_228/data.json", "r") as f:
    data = json.load(f)

GuestsPerMinDense = data["GuestsPerMinDense"] # scalar parameter
GuestsPerMinLoose = data["GuestsPerMinLoose"] # scalar parameter
ElectricityDense = data["ElectricityDense"] # scalar parameter
ElectricityLoose = data["ElectricityLoose"] # scalar parameter
MinLooseLifts = data["MinLooseLifts"] # scalar parameter
MinGuestsPerMin = data["MinGuestsPerMin"] # scalar parameter
TotalElectricity = data["TotalElectricity"] # scalar parameter
NumberOfDenseLifts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfDenseLifts")
NumberOfLooseLifts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberOfLooseLifts")

# The non-negativity constraint is automatically ensured due to the default non-negative domain of continuous variables in Gurobi.

# Add non-negativity constraint for the NumberOfLooseLifts
model.addConstr(NumberOfLooseLifts >= 0, name="non_negative_loose_lifts")

# Add constraint to ensure the number of loosely-seated ski lifts meets the minimum required
model.addConstr(NumberOfLooseLifts >= MinLooseLifts, name="min_loose_lifts_constraint")

# Add constraint to ensure the combined number of guests transported per minute meets the minimum requirement
model.addConstr(
    NumberOfDenseLifts * GuestsPerMinDense + NumberOfLooseLifts * GuestsPerMinLoose >= MinGuestsPerMin,
    name="min_guests_per_min"
)

# Add electricity usage constraint for ski lifts
model.addConstr(ElectricityDense * NumberOfDenseLifts + ElectricityLoose * NumberOfLooseLifts <= TotalElectricity, name="electricity_usage_constraint")

# Add constraint to ensure the total guests transported meets the minimum requirement
model.addConstr(
    GuestsPerMinDense * NumberOfDenseLifts + GuestsPerMinLoose * NumberOfLooseLifts >= MinGuestsPerMin,
    name="min_guest_transportation"
)

# Add electricity usage constraint for ski lifts
model.addConstr(
    NumberOfDenseLifts * ElectricityDense + NumberOfLooseLifts * ElectricityLoose <= TotalElectricity,
    name="electricity_usage_constraint"
)

# Add constraint to ensure the number of loosely-seated ski lifts meets the minimum required
model.addConstr(NumberOfLooseLifts >= MinLooseLifts, name="min_loose_lifts")

# Set objective
model.setObjective(NumberOfDenseLifts + NumberOfLooseLifts, gp.GRB.MINIMIZE)

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
