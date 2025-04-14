import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_113/data.json", "r") as f:
    data = json.load(f)

TotalMRna = data["TotalMRna"] # scalar parameter
MRnaPerChildVaccine = data["MRnaPerChildVaccine"] # scalar parameter
MRnaPerAdultVaccine = data["MRnaPerAdultVaccine"] # scalar parameter
FeverSuppressantPerChildVaccine = data["FeverSuppressantPerChildVaccine"] # scalar parameter
FeverSuppressantPerAdultVaccine = data["FeverSuppressantPerAdultVaccine"] # scalar parameter
MinAdultVaccineProp = data["MinAdultVaccineProp"] # scalar parameter
MinChildVaccines = data["MinChildVaccines"] # scalar parameter
ChildVaccines = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ChildVaccines")
AdultVaccines = model.addVar(vtype=gp.GRB.CONTINUOUS, name="AdultVaccines")

# Add constraint to ensure mRNA usage does not exceed TotalMRna
model.addConstr(
    MRnaPerChildVaccine * ChildVaccines + MRnaPerAdultVaccine * AdultVaccines <= TotalMRna,
    name="mRNA_usage_limit"
)

# Add constraint to ensure at least MinAdultVaccineProp of the vaccines are adult vaccines
model.addConstr((1 - MinAdultVaccineProp) * AdultVaccines >= MinAdultVaccineProp * ChildVaccines, 
                name="adult_vaccine_proportion")

# Add minimum production constraint for children's vaccines
model.addConstr(ChildVaccines >= MinChildVaccines, name="min_child_vaccines")

# Add mRNA supply constraint
model.addConstr(
    MRnaPerChildVaccine * ChildVaccines + MRnaPerAdultVaccine * AdultVaccines <= TotalMRna,
    name="mRNA_supply_constraint"
)

# Add constraint to ensure the proportion of adult vaccines meets the minimum required proportion
model.addConstr(AdultVaccines * (1 - MinAdultVaccineProp) >= MinAdultVaccineProp * ChildVaccines, name="min_adult_vaccine_proportion")

# Add constraint ensuring the production of children's vaccines meets the minimum requirement
model.addConstr(ChildVaccines >= MinChildVaccines, name="min_child_vaccines")

# Set objective
model.setObjective(
    FeverSuppressantPerChildVaccine * ChildVaccines + FeverSuppressantPerAdultVaccine * AdultVaccines,
    gp.GRB.MINIMIZE
)

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
