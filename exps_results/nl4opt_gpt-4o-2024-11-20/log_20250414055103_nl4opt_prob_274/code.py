import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_274/data.json", "r") as f:
    data = json.load(f)

AntibioticsAvailable = data["AntibioticsAvailable"] # scalar parameter
AntibioticsFirstDose = data["AntibioticsFirstDose"] # scalar parameter
AntibioticsSecondDose = data["AntibioticsSecondDose"] # scalar parameter
GelatineFirstDose = data["GelatineFirstDose"] # scalar parameter
GelatineSecondDose = data["GelatineSecondDose"] # scalar parameter
MinimumSecondDose = data["MinimumSecondDose"] # scalar parameter
FirstDoseProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="FirstDoseProduced")
SecondDoseProduced = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SecondDoseProduced")

# Adding constraint: The number of first-dose vaccines is non-negative
model.addConstr(FirstDoseProduced >= 0, name="non_negative_constraint")

# Add non-negativity constraint for SecondDoseProduced
model.addConstr(SecondDoseProduced >= 0, name="nonnegativity_constraint")

# Add constraint to limit total antibiotics usage
model.addConstr(
    AntibioticsFirstDose * FirstDoseProduced + AntibioticsSecondDose * SecondDoseProduced <= AntibioticsAvailable,
    name="antibiotics_usage_limit"
)

# Add constraint to ensure the number of first-dose vaccines produced exceeds the second-dose vaccines produced by at least 1
model.addConstr(FirstDoseProduced - SecondDoseProduced >= 1, name="first_vs_second_dose")

# Add constraint ensuring at least the minimum number of second-dose vaccines are produced
model.addConstr(SecondDoseProduced >= MinimumSecondDose, name="min_second_dose")

# Add constraint to ensure production of first-dose vaccines exceeds second-dose vaccines
model.addConstr(FirstDoseProduced >= SecondDoseProduced + 1, name="first_dose_greater_than_second_dose")

# Add constraint to ensure the production of second-dose vaccines meets the minimum requirement
model.addConstr(SecondDoseProduced >= MinimumSecondDose, name="second_dose_min_constraint")

# Add the minimum production constraint for second-dose vaccines
model.addConstr(SecondDoseProduced >= MinimumSecondDose, name="min_second_dose_constraint")

# Add total antibiotic consumption constraint
model.addConstr(
    FirstDoseProduced * AntibioticsFirstDose + SecondDoseProduced * AntibioticsSecondDose <= AntibioticsAvailable,
    name="antibiotic_consumption"
)

# Add constraint to enforce minimum production of second-dose vaccines
model.addConstr(SecondDoseProduced >= MinimumSecondDose, name="min_second_dose_constraint")

# Add constraint: First dose production must be strictly greater than second dose production
model.addConstr(FirstDoseProduced >= SecondDoseProduced + 1, name="first_dose_greater_than_second")

# Set objective
model.setObjective(GelatineFirstDose * FirstDoseProduced + GelatineSecondDose * SecondDoseProduced, gp.GRB.MINIMIZE)

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
