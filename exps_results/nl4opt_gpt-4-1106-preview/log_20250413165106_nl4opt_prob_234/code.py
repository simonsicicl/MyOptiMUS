import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_234/data.json", "r") as f:
    data = json.load(f)

TechnicianHoursPerShift = data["TechnicianHoursPerShift"] # scalar parameter
ResearcherHoursPerShift = data["ResearcherHoursPerShift"] # scalar parameter
TechnicianPaymentPerShift = data["TechnicianPaymentPerShift"] # scalar parameter
ResearcherPaymentPerShift = data["ResearcherPaymentPerShift"] # scalar parameter
RequiredTechnicianToResearcherRatio = data["RequiredTechnicianToResearcherRatio"] # scalar parameter
TotalUltrasoundHoursNeeded = data["TotalUltrasoundHoursNeeded"] # scalar parameter
TotalBudget = data["TotalBudget"] # scalar parameter
UltrasoundTechnicianShifts = model.addVar(vtype=gp.GRB.INTEGER, name="UltrasoundTechnicianShifts")
GraduateResearcherShifts = model.addVar(vtype=gp.GRB.INTEGER, name="GraduateResearcherShifts")

# No code needed since the variable UltrasoundTechnicianShifts is already defined as non-negative integer
# by the `addVar` method with default lower bound 0.

# Since the variable GraduateResearcherShifts is already non-negative by default,
# no additional constraint is necessary.

# Add constraint for the ratio of ultrasound technician shifts to graduate researcher shifts
UltrasoundTechnicianShifts = model.addVar(vtype=gp.GRB.INTEGER, name="UltrasoundTechnicianShifts")
GraduateResearcherShifts = model.addVar(vtype=gp.GRB.INTEGER, name="GraduateResearcherShifts")
RequiredTechnicianToResearcherRatio = data["RequiredTechnicianToResearcherRatio"]  # Assuming data is a predefined dictionary

model.addConstr(UltrasoundTechnicianShifts == RequiredTechnicianToResearcherRatio * GraduateResearcherShifts, name="tech_to_researcher_ratio")

# Constraint: Total cost of hiring ultrasound technicians and graduate researchers should not exceed the TotalBudget
model.addConstr(UltrasoundTechnicianShifts * TechnicianPaymentPerShift + GraduateResearcherShifts * ResearcherPaymentPerShift <= TotalBudget, "budget_constraint")

# Ensure that the total hours of ultrasound service meet the required hours
model.addConstr(TechnicianHoursPerShift * UltrasoundTechnicianShifts + ResearcherHoursPerShift * GraduateResearcherShifts >= TotalUltrasoundHoursNeeded, "total_ultrasound_service_hours")

# Ensure that the cost of hiring technicians and researchers does not exceed the total budget
model.addConstr(TechnicianPaymentPerShift * UltrasoundTechnicianShifts + ResearcherPaymentPerShift * GraduateResearcherShifts <= TotalBudget, "budget_constraint")

# Ensure that the ratio of ultrasound technician shifts to graduate researcher shifts meets the required ratio
model.addConstr(UltrasoundTechnicianShifts >= RequiredTechnicianToResearcherRatio * GraduateResearcherShifts, "ratio_ultrasound_technician_to_graduate_researcher")

# Set objective
model.setObjective(UltrasoundTechnicianShifts + GraduateResearcherShifts, gp.GRB.MINIMIZE)

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
