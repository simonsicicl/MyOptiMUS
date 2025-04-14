import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_261/data.json", "r") as f:
    data = json.load(f)

MotorcycleCapacity = data["MotorcycleCapacity"] # scalar parameter
MotorcyclePollution = data["MotorcyclePollution"] # scalar parameter
MotorcycleEarnings = data["MotorcycleEarnings"] # scalar parameter
SedanCapacity = data["SedanCapacity"] # scalar parameter
SedanPollution = data["SedanPollution"] # scalar parameter
SedanEarnings = data["SedanEarnings"] # scalar parameter
MaxMotorcycleProportion = data["MaxMotorcycleProportion"] # scalar parameter
MaxPollution = data["MaxPollution"] # scalar parameter
MinPeopleTransported = data["MinPeopleTransported"] # scalar parameter
NumberOfMotorcycles = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfMotorcycles")
NumberOfSedans = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfSedans")

# Add constraint to ensure the number of motorcycles is non-negative
model.addConstr(NumberOfMotorcycles >= 0, name="non_negative_motorcycles")

# Since NumberOfSedans has already been defined as an integer variable, 
# we just need to add a constraint to ensure it is non-negative.
model.addConstr(NumberOfSedans >= 0, name="number_of_sedans_nonneg")

# Motorcycle proportion constraints
model.addConstr(NumberOfMotorcycles <= MaxMotorcycleProportion * (NumberOfMotorcycles + NumberOfSedans), name="MaxMotorcycleProportionConstraint")

# Total pollution constraint
model.addConstr(NumberOfMotorcycles * MotorcyclePollution + NumberOfSedans * SedanPollution <= MaxPollution, "Total_pollution_constraint")

# Ensure that the company can transport at least the minimum number of people every shift
model.addConstr(NumberOfMotorcycles * MotorcycleCapacity + NumberOfSedans * SedanCapacity >= MinPeopleTransported, "min_people_transported")

# Add constraint for the maximum proportion of motorcycles in the fleet
model.addConstr(NumberOfMotorcycles <= MaxMotorcycleProportion * (NumberOfMotorcycles + NumberOfSedans), name="max_motorcycle_proportion")

# Total pollution from all vehicles should not exceed the maximum allowed pollution per shift
model.addConstr(MotorcyclePollution * NumberOfMotorcycles + SedanPollution * NumberOfSedans <= MaxPollution, "MaxPollutionConstraint")

# Add constraint for total capacity to meet or exceed the minimum required to transport people per shift
model.addConstr(MotorcycleCapacity * NumberOfMotorcycles + SedanCapacity * NumberOfSedans >= MinPeopleTransported, name="people_transport_capacity")

# Define the objective function
model.setObjective(MotorcycleEarnings * NumberOfMotorcycles + SedanEarnings * NumberOfSedans, gp.GRB.MAXIMIZE)

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
