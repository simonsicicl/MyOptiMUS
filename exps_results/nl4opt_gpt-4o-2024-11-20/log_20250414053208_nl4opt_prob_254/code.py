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
NumberLargeBags = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberLargeBags")
NumberTinyBags = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberTinyBags")

# The variable "NumberLargeBags" is already defined as non-negative due to its default lower bound (0) in Gurobi.
# No additional code needed.

# The variable "NumberTinyBags" is already defined as non-negative (continuous and defaults to >= 0), so no additional constraints are needed.

# Add energy usage constraint for transporting bags
model.addConstr(
    LargeBagEnergy * NumberLargeBags + TinyBagEnergy * NumberTinyBags <= TotalEnergy,
    name="energy_constraint"
)

# Add a constraint to ensure the number of large bags is twice the number of tiny bags
model.addConstr(NumberLargeBags == 2 * NumberTinyBags, name="large_bags_twice_tiny")

# Add constraint to ensure the number of transported tiny bags is at least MinTinyBags
model.addConstr(NumberTinyBags >= MinTinyBags, name="min_tiny_bags_constraint")

# Add ratio constraint for large bags relative to tiny bags
model.addConstr(NumberLargeBags == BagRatio * NumberTinyBags, name="large_to_tiny_bag_ratio")

# Add constraint to ensure total energy used for transportation does not exceed available energy
model.addConstr(LargeBagEnergy * NumberLargeBags + TinyBagEnergy * NumberTinyBags <= TotalEnergy, name="energy_constraint")

# Add the constraint to ensure the number of tiny bags satisfies the minimum requirement
model.addConstr(NumberTinyBags >= MinTinyBags, name="min_tiny_bags_req")

# Add constraint for the relationship between large bags and tiny bags
model.addConstr(NumberLargeBags == BagRatio * NumberTinyBags, name="large_to_tiny_bag_ratio")

# Add constraint to ensure the number of tiny bags is at least the minimum required
model.addConstr(NumberTinyBags >= MinTinyBags, name="min_tiny_bags_constraint")

# Add total energy usage constraint
model.addConstr((NumberLargeBags * LargeBagEnergy) + (NumberTinyBags * TinyBagEnergy) <= TotalEnergy, 
                name="total_energy_constraint")

# Add ratio constraint for large bags and tiny bags
model.addConstr(NumberLargeBags == BagRatio * NumberTinyBags, name="BagRatioConstraint")

# Add constraint ensuring the number of tiny bags transported is at least the minimum required
model.addConstr(NumberTinyBags >= MinTinyBags, name="min_tiny_bags_requirement")

# Set objective
model.setObjective((NumberLargeBags * LargeBagCapacity) + (NumberTinyBags * TinyBagCapacity), gp.GRB.MAXIMIZE)

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
