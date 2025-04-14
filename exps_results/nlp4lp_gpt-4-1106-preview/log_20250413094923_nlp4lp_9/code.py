import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/9/data.json", "r") as f:
    data = json.load(f)

K = data["K"] # scalar parameter
P = np.array(data["P"]) # ['K']
ExpectedZ = data["ExpectedZ"] # scalar parameter
ExpectedZSquared = data["ExpectedZSquared"] # scalar parameter
ExpectedZToFourth = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ExpectedZToFourth")

# Variable K is already non-negative by definition, no additional constraint needed.

# Define decision variables for array P\nvars_P = model.addVars(K, name='P', lb=0)\n\n# Non-negativity constraint for array P is now implicit in the variable definition with lb=0\n# No need to add additional constraints.

# No need to add a constraint as the formulation "E[Z^4] >= 0" is inherently satisfied by the definition of expected value and non-negativity of powers
# However, if you would like to include this in the model for some reason (e.g., as documentation), you can create an auxiliary variable and constrain it to be non-negative and represent E[Z^4]

# First, ensure we import gurobipy as gp and read data from some source
# from gurobipy import Model, GRB
# data = some_data_source()

# Assume ExpectedZ and ExpectedZSquared are read from 'data' and are both non-negative

model = gp.Model("OptimizationModel")

# Define the auxiliary variable for E[Z^4] (assuming no other characteristics for the variable are needed)
EZ4 = model.addVar(name="EZ4", lb=0, vtype=gp.GRB.CONTINUOUS)

# Here, we already know ExpectedZ and ExpectedZSquared from our data, but we don't necessarily have a value for E[Z^4].
# If you do have a specific value in mind or a relationship involving E[Z^4], you could include an additional constraint.
# Otherwise, you merely need to define the variable as being non-negative, which has been done above with lb=0 when defining EZ4.

ExpectedZToFourth = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ExpectedZToFourth")
model.update()  # Ensure variables are integrated into the model before using them in constraints

# Define the auxiliary constraint for the fourth moment correctly
model.addConstr(ExpectedZToFourth - ExpectedZSquared**2 <= 0, name="fourth_moment_constraint")

# Ensure that the fourth moment is consistent with the given first and second moments
model.addConstr(ExpectedZToFourth >= ExpectedZ**4, name="consistency_fourth_moment")

# Set objective for minimization
model.setObjective(ExpectedZToFourth, gp.GRB.MINIMIZE)

# Set objective for maximization
# model.setObjective(ExpectedZToFourth, gp.GRB.MAXIMIZE)

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
