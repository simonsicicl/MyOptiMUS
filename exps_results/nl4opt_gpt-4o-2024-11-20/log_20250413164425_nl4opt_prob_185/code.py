import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_185/data.json", "r") as f:
    data = json.load(f)

LabradorNewspaperCount = data["LabradorNewspaperCount"] # scalar parameter
LabradorBoneTreatCount = data["LabradorBoneTreatCount"] # scalar parameter
GoldenRetrieverNewspaperCount = data["GoldenRetrieverNewspaperCount"] # scalar parameter
GoldenRetrieverBoneTreatCount = data["GoldenRetrieverBoneTreatCount"] # scalar parameter
TotalBoneTreatsAvailable = data["TotalBoneTreatsAvailable"] # scalar parameter
MinGoldenRetrievers = data["MinGoldenRetrievers"] # scalar parameter
MaxLabradorProportion = data["MaxLabradorProportion"] # scalar parameter
NumberLabradors = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberLabradors")
NumberGoldenRetrievers = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberGoldenRetrievers")
TotalDogs = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalDogs")

# Add constraint for non-negativity of the number of labradors
model.addConstr(NumberLabradors >= 0, name="non_negative_labradors")

# Add constraint to ensure the number of golden retrievers is non-negative
model.addConstr(NumberGoldenRetrievers >= 0, name="non_negative_golden_retrievers")

# Add constraint for the total number of bone treats used
model.addConstr(
    LabradorBoneTreatCount * NumberLabradors + GoldenRetrieverBoneTreatCount * NumberGoldenRetrievers <= TotalBoneTreatsAvailable,
    name="bone_treats_constraint"
)

# Add constraint to ensure at least MinGoldenRetrievers golden retrievers are used
model.addConstr(NumberGoldenRetrievers >= MinGoldenRetrievers, name="min_golden_retrievers")

# Add constraint ensuring at most MaxLabradorProportion of dogs are labradors
model.addConstr((1 - MaxLabradorProportion) * NumberLabradors <= MaxLabradorProportion * NumberGoldenRetrievers, name="max_labrador_proportion")

# Add constraint for total bone treat usage
model.addConstr(
    LabradorBoneTreatCount * NumberLabradors + GoldenRetrieverBoneTreatCount * NumberGoldenRetrievers <= TotalBoneTreatsAvailable,
    name="bone_treats_constraint"
)

# Add constraint to ensure the number of golden retrievers meets the minimum requirement  
model.addConstr(NumberGoldenRetrievers >= MinGoldenRetrievers, name="min_golden_retrievers")

# Add constraint to ensure the proportion of labradors does not exceed the maximum allowable proportion
model.addConstr(NumberLabradors <= MaxLabradorProportion * TotalDogs, name="MaxLabradorProportionConstraint")

# Add constraint defining TotalDogs as the sum of NumberLabradors and NumberGoldenRetrievers
model.addConstr(TotalDogs == NumberLabradors + NumberGoldenRetrievers, name="total_dogs_sum")

# Set objective
model.setObjective(LabradorNewspaperCount * NumberLabradors + GoldenRetrieverNewspaperCount * NumberGoldenRetrievers, gp.GRB.MAXIMIZE)

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
