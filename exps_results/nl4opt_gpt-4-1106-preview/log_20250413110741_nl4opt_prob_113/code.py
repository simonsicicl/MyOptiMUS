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
NumberOfChildVaccines = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfChildVaccines")
NumberOfAdultVaccines = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfAdultVaccines")

# Add mRNA total usage constraint
model.addConstr(MRnaPerChildVaccine * NumberOfChildVaccines + MRnaPerAdultVaccine * NumberOfAdultVaccines <= TotalMRna, name="total_mrna_usage")

# Adult vaccine proportion constraint
model.addConstr(NumberOfAdultVaccines >= MinAdultVaccineProp * (NumberOfAdultVaccines + NumberOfChildVaccines), name="adult_vaccine_proportion")

# Add constraint for minimum number of children's vaccines to be produced
model.addConstr(NumberOfChildVaccines >= MinChildVaccines, name="min_children_vaccines")

# Ensure that the total amount of mRNA anti-viral used does not exceed the available amount
model.addConstr(MRnaPerChildVaccine * NumberOfChildVaccines + MRnaPerAdultVaccine * NumberOfAdultVaccines <= TotalMRna, name="TotalMRnaConstraint")

# Ensure that a minimum proportion of vaccines are for adults
model.addConstr(NumberOfAdultVaccines >= MinAdultVaccineProp * (NumberOfChildVaccines + NumberOfAdultVaccines), name="min_adult_vaccine_proportion")

# Ensure that a minimum number of children's vaccines are produced
model.addConstr(NumberOfChildVaccines >= MinChildVaccines, name="min_children_vaccines")

# Set objective
model.setObjective(FeverSuppressantPerChildVaccine * NumberOfChildVaccines + FeverSuppressantPerAdultVaccine * NumberOfAdultVaccines, gp.GRB.MINIMIZE)

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
