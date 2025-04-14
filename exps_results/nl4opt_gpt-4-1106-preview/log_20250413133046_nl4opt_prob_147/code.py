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
NumberOfBeamBridges = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfBeamBridges")
NumberOfTrussBridges = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTrussBridges")

# Since NumberOfBeamBridges is already guaranteed to be non-negative by its variable type definition,
# no additional constraint is needed.
# The variable is an integer and Gurobi, by default, does not allow negative values for integer variables.

# Since the variable NumberOfTrussBridges is already ensured to be an integer, we only need to add a constraint to enforce its non-negativity.
model.addConstr(NumberOfTrussBridges >= 0, name="truss_bridge_nonnegativity")

# Total use of Popsicle sticks must not exceed the total available Popsicle sticks
model.addConstr(NumberOfBeamBridges * PopsicleBeam + NumberOfTrussBridges * PopsicleTruss <= TotalPopsicles, 
                name="Popsicle_Stick_Usage")

# Add constraint for the total consumption of glue for building bridges
model.addConstr(
    GlueBeam * NumberOfBeamBridges + GlueTruss * NumberOfTrussBridges <= TotalGlue,
    name="glue_consumption"
)

# Add truss bridge constraint
model.addConstr(NumberOfTrussBridges <= MaxTruss, name="max_truss_bridges")

# Add constraint: Number of beam bridges must be greater than the number of truss bridges by at least one
model.addConstr(NumberOfBeamBridges >= NumberOfTrussBridges + 1, name="beam_vs_truss_constraint")

# Constraint: The total number of Popsicle sticks used should not exceed the total available Popsicle sticks
model.addConstr(PopsicleBeam * NumberOfBeamBridges + PopsicleTruss * NumberOfTrussBridges <= TotalPopsicles, name="Popsicle_Stick_Usage")

GlueBeam = data["GlueBeam"]  # scalar parameter
GlueTruss = data["GlueTruss"]  # scalar parameter
TotalGlue = data["TotalGlue"]  # scalar parameter

# Add constraint for total units of glue used not to exceed total available units of glue
model.addConstr(GlueBeam * NumberOfBeamBridges + GlueTruss * NumberOfTrussBridges <= TotalGlue, name="total_glue_usage")

# Constraint: Number of truss bridges should not exceed the maximum allowed
model.addConstr(NumberOfTrussBridges <= MaxTruss, "truss_bridge_limit")

# Define the objective function
TotalSupportedMass = MassBeam * NumberOfBeamBridges + MassTruss * NumberOfTrussBridges

# Set objective
model.setObjective(TotalSupportedMass, gp.GRB.MAXIMIZE)

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
