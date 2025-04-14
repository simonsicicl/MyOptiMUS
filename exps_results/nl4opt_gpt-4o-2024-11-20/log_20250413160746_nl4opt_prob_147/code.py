import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_147/data.json", "r") as f:
    data = json.load(f)

PopsicleBeam = data["PopsicleBeam"] # scalar parameter
GlueBeam = data["GlueBeam"] # scalar parameter
PopsicleTruss = data["PopsicleTruss"] # scalar parameter
GlueTruss = data["GlueTruss"] # scalar parameter
TotalPopsicles = data["TotalPopsicles"] # scalar parameter
TotalGlue = data["TotalGlue"] # scalar parameter
MaxTruss = data["MaxTruss"] # scalar parameter
MassBeam = data["MassBeam"] # scalar parameter
MassTruss = data["MassTruss"] # scalar parameter
NumberBeam = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberBeam")
NumberTruss = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberTruss")

# No code needed: The variable "NumberBeam" is already constrained to be non-negative by default as it is defined as a continuous variable.

# Non-negativity constraint for NumberTruss
model.addConstr(NumberTruss >= 0, name="non_negativity_NumberTruss")

# Add constraint to ensure the total Popsicle sticks used does not exceed the available supply
model.addConstr(
    NumberBeam * PopsicleBeam + NumberTruss * PopsicleTruss <= TotalPopsicles, 
    name="Popsicle_limit"
)

# Add constraint for glue consumption
model.addConstr(GlueBeam * NumberBeam + GlueTruss * NumberTruss <= TotalGlue, name="glue_consumption")

# Ensure NumberTruss is not greater than MaxTruss
model.addConstr(NumberTruss <= MaxTruss, name="limit_truss_bridges")

# Add constraint ensuring the number of beam bridges must be at least one greater than the number of truss bridges
model.addConstr(NumberBeam >= NumberTruss + 1, name="beam_greater_than_truss")

# Add constraint for total Popsicle stick usage
model.addConstr(
    NumberBeam * PopsicleBeam + NumberTruss * PopsicleTruss <= TotalPopsicles,
    name="Popsicle_usage_constraint"
)

# Add constraint to limit total glue consumption
model.addConstr(
    NumberBeam * GlueBeam + NumberTruss * GlueTruss <= TotalGlue, 
    name="glue_limit"
)

# Add constraint to ensure the number of truss bridges does not exceed the maximum allowed
model.addConstr(NumberTruss <= MaxTruss, name="max_truss_constraint")

# No code needed as the non-negativity constraint is automatically satisfied by gurobipy when the variables are defined with vtype=gp.GRB.CONTINUOUS.

# Set objective
model.setObjective(MassBeam * NumberBeam + MassTruss * NumberTruss, gp.GRB.MAXIMIZE)

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
