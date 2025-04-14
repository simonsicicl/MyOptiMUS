import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_237/data.json", "r") as f:
    data = json.load(f)

PopAudience = data["PopAudience"] # scalar parameter
PopPracticeDays = data["PopPracticeDays"] # scalar parameter
RbAudience = data["RbAudience"] # scalar parameter
RbPracticeDays = data["RbPracticeDays"] # scalar parameter
MinAudience = data["MinAudience"] # scalar parameter
AvailablePracticeDays = data["AvailablePracticeDays"] # scalar parameter
MaxRbConcertsProportion = data["MaxRbConcertsProportion"] # scalar parameter
PopConcerts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="PopConcerts")
RbConcerts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="RbConcerts")

# The variable PopConcerts already has non-negativity implicitly enforced due to its default lower bound (0) in Gurobi.

# Add non-negativity constraint for RbConcerts
model.addConstr(RbConcerts >= 0, name="non_negativity_RbConcerts")

# Add audience member constraint
model.addConstr(PopConcerts * PopAudience + RbConcerts * RbAudience >= MinAudience, name="min_audience_constraint")

# Add constraint to ensure total practice days for pop and R&B concerts do not exceed available practice days
model.addConstr(
    PopPracticeDays * PopConcerts + RbPracticeDays * RbConcerts <= AvailablePracticeDays,
    name="practice_days_constraint"
)

# Add constraint linking RbConcerts and PopConcerts to MaxRbConcertsProportion
model.addConstr((1 - MaxRbConcertsProportion) * RbConcerts <= MaxRbConcertsProportion * PopConcerts, name="max_rb_concerts_proportion")

# Add minimum total audience constraint
model.addConstr(
    PopAudience * PopConcerts + RbAudience * RbConcerts >= MinAudience,
    name="min_audience_constraint"
)

# Add practice days constraint
model.addConstr(
    PopPracticeDays * PopConcerts + RbPracticeDays * RbConcerts <= AvailablePracticeDays, 
    name="practice_days_constraint"
)

# Add maximum proportion of R&B concerts constraint
model.addConstr(
    RbConcerts <= (MaxRbConcertsProportion / (1 - MaxRbConcertsProportion)) * PopConcerts, 
    name="max_rb_concerts_proportion"
)

# Set objective
model.setObjective(PopConcerts + RbConcerts, gp.GRB.MINIMIZE)

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
