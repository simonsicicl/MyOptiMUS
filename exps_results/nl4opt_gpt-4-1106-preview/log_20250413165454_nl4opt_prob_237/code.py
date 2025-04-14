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
PopConcerts = model.addVar(vtype=gp.GRB.INTEGER, name="PopConcerts")
RbConcerts = model.addVar(vtype=gp.GRB.INTEGER, name="RbConcerts")

model.addConstr(PopConcerts >= 0, "pop_concerts_nonnegativity")

# Add non-negativity constraint for the number of R&B concerts
model.addConstr(RbConcerts >= 0, name="RbConcerts_nonnegativity")

# Total audience constraint for pop and R&B concerts
model.addConstr(PopConcerts * PopAudience + RbConcerts * RbAudience >= MinAudience, name="min_audience_requirement")

# Constraint: Total practice days for pop concerts and R&B concerts must not exceed AvailablePracticeDays
model.addConstr(PopConcerts * PopPracticeDays + RbConcerts * RbPracticeDays <= AvailablePracticeDays, "PracticeDaysLimit")

# Add constraint for the number of R&B concerts not to exceed the maximum proportion allowed
model.addConstr(RbConcerts <= MaxRbConcertsProportion * (PopConcerts + RbConcerts), name="max_rb_concerts_proportion")

# Constraint: The total number of audience members from both types of concerts should be at least the minimum required
model.addConstr(PopConcerts * PopAudience + RbConcerts * RbAudience >= MinAudience, name="min_audience_requirement")

# Add constraint for total practice days for all concerts not to exceed available practice days
model.addConstr(PopConcerts * PopPracticeDays + RbConcerts * RbPracticeDays <= AvailablePracticeDays, name="practice_days_limit")

# The number of R&B concerts cannot exceed the maximum proportion allowed of the total concerts held
model.addConstr(RbConcerts <= MaxRbConcertsProportion * (PopConcerts + RbConcerts), "RbConcerts_proportion_constraint")

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
