import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_254/data.json", "r") as f:
    data = json.load(f)

LargeBagCapacity = data["LargeBagCapacity"] # scalar parameter
LargeBagEnergy = data["LargeBagEnergy"] # scalar parameter
TinyBagCapacity = data["TinyBagCapacity"] # scalar parameter
TinyBagEnergy = data["TinyBagEnergy"] # scalar parameter
TotalEnergy = data["TotalEnergy"] # scalar parameter
BagRatio = data["BagRatio"] # scalar parameter
MinTinyBags = data["MinTinyBags"] # scalar parameter
NumberOfLargeBags = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfLargeBags")
NumberOfTinyBags = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTinyBags")

# Since the variable NumberOfLargeBags has already been defined as an integer variable, 
# the non-negativity constraint is implicitly applied.
# Hence, no code is needed for this constraint.

# Since NumberOfTinyBags has already been defined as an integer variable, 
# we only need to ensure its non-negativity, which is inherent in the GUROBI integer variable definition.
# No additional code is required for the non-negativity constraint.

# Add constraint for total energy used for transporting bags
model.addConstr((NumberOfLargeBags * LargeBagEnergy) + (NumberOfTinyBags * TinyBagEnergy) <= TotalEnergy, name="TotalEnergyConstraint")

# Constraint: The number of large bags must be twice the number of tiny bags
model.addConstr(NumberOfLargeBags == 2 * NumberOfTinyBags, name="large_bags_twice_tiny_bags")

# Add constraint to ensure the number of tiny bags is at least the minimum required
model.addConstr(NumberOfTinyBags >= MinTinyBags, name="min_tiny_bags")

# Add constraint enforcing twice as many large bags as tiny bags
model.addConstr(NumberOfLargeBags == 2 * NumberOfTinyBags, name="demand_ratio_large_to_tiny")

# Constraint for the minimum number of tiny bags required
model.addConstr(NumberOfTinyBags >= MinTinyBags, name="min_tiny_bags")

# Demand ratio constraint for twice as many large bags as tiny bags
model.addConstr(NumberOfLargeBags == 2 * NumberOfTinyBags, name="demand_ratio")

# Constraint for the minimum number of tiny bags required
model.addConstr(NumberOfTinyBags >= MinTinyBags, name="min_tiny_bags_required")

# Energy constraint to ensure the total energy used for transporting bags does not exceed the available energy
model.addConstr(NumberOfLargeBags * LargeBagEnergy + NumberOfTinyBags * TinyBagEnergy <= TotalEnergy, name="energy_constraint")

# Maintain the required ratio of large bags to tiny bags
model.addConstr(NumberOfLargeBags == BagRatio * NumberOfTinyBags, name="large_to_tiny_bag_ratio")

# Add constraint to ensure the number of tiny bags meets the minimum requirement
model.addConstr(NumberOfTinyBags >= MinTinyBags, name="min_tiny_bags_requirement")

# Define objective function
objective = (NumberOfLargeBags * LargeBagCapacity) + (NumberOfTinyBags * TinyBagCapacity)

# Set the objective in the model
model.setObjective(objective, gp.GRB.MAXIMIZE)

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
