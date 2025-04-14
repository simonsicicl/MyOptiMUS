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
NumberOfLabradors = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLabradors")
NumberOfGoldenRetrievers = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfGoldenRetriebers")

# The number of labradors must be non-negative
model.addConstr(NumberOfLabradors >= 0, name="non_negative_labradors")

# The number of golden retrievers must be non-negative
# Since NumberOfGoldenRetrievers is already added as an integer variable, no further constraint is needed.
# This constraint is inherently satisfied by the variable's type.

# Total bone treats used by labradors and golden retrievers cannot exceed TotalBoneTreatsAvailable
model.addConstr(NumberOfLabradors * LabradorBoneTreatCount +
                NumberOfGoldenRetrievers * GoldenRetrieverBoneTreatCount <= TotalBoneTreatsAvailable,
                name="bone_treats_limit")

# At least the minimum number of golden retrievers must be used in the dog school program
model.addConstr(NumberOfGoldenRetrievers >= MinGoldenRetrievers, name="min_golden_retrievers")

# Labrador proportion constraint
model.addConstr(NumberOfLabradors <= MaxLabradorProportion * (NumberOfLabradors + NumberOfGoldenRetrievers), name="LabradorProportionConstraint")

# Total number of bone treats used by labradors and golden retrievers should not exceed the available bone treats
model.addConstr(LabradorBoneTreatCount * NumberOfLabradors + GoldenRetrieverBoneTreatCount * NumberOfGoldenRetrievers <= TotalBoneTreatsAvailable, name="bone_treats_limit")

NumberOfGoldenRetrievers = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfGoldenRetrievers")

# Proportion of labradors constraint
model.addConstr(NumberOfLabradors <= MaxLabradorProportion * (NumberOfLabradors + NumberOfGoldenRetrievers), name="labrador_proportion")

# Set objective
model.setObjective(LabradorNewspaperCount * NumberOfLabradors + GoldenRetrieverNewspaperCount * NumberOfGoldenRetrievers, gp.GRB.MAXIMIZE)

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
