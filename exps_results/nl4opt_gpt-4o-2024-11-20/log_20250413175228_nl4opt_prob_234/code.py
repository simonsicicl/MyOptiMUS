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
TechnicianShifts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TechnicianShifts")
ResearcherShifts = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ResearcherShifts")

# The variable "TechnicianShifts" is non-negative by default since it is a continuous variable.

# Non-negativity constraint for the number of graduate researcher shifts
model.addConstr(ResearcherShifts >= 0, name="non_negative_researcher_shifts")

# Add equality constraint to ensure the ratio of technician shifts to researcher shifts matches the required ratio
model.addConstr(TechnicianShifts == RequiredTechnicianToResearcherRatio * ResearcherShifts, name="technician_researcher_ratio")

# Add total expenditure constraint
model.addConstr(
    TechnicianPaymentPerShift * TechnicianShifts + ResearcherPaymentPerShift * ResearcherShifts <= TotalBudget,
    name="total_expenditure_constraint"
)

# Add constraint to ensure technician shifts are only scheduled if researcher shifts are scheduled
model.addConstr((ResearcherShifts == 0) >> (TechnicianShifts == 0), name="no_technician_without_researcher")

# Add constraint to ensure total service hours meet or exceed the required ultrasound hours
model.addConstr(
    TechnicianShifts * TechnicianHoursPerShift + ResearcherShifts * ResearcherHoursPerShift >= TotalUltrasoundHoursNeeded,
    name="total_service_hours_constraint"
)

# Add a budget constraint to ensure worker payments do not exceed the budget
model.addConstr(
    TechnicianShifts * TechnicianPaymentPerShift + ResearcherShifts * ResearcherPaymentPerShift <= TotalBudget,
    name="budget_constraint"
)

# Add constraint to maintain the required ratio of ultrasound technician shifts to graduate researcher shifts
model.addConstr(TechnicianShifts >= RequiredTechnicianToResearcherRatio * ResearcherShifts, 
                name="TechnicianToResearcherRatio")

# Set objective
model.setObjective(TechnicianShifts + ResearcherShifts, gp.GRB.MINIMIZE)

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
