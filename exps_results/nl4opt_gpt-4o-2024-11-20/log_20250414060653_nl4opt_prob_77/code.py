import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_77/data.json", "r") as f:
    data = json.load(f)

DualCap = data["DualCap"] # scalar parameter
SingleCap = data["SingleCap"] # scalar parameter
DualGlue = data["DualGlue"] # scalar parameter
SingleGlue = data["SingleGlue"] # scalar parameter
MinLetters = data["MinLetters"] # scalar parameter
MaxGlue = data["MaxGlue"] # scalar parameter
DualMachineCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="DualMachineCount")
SingleMachineCount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="SingleMachineCount")

# Update the variable type of DualMachineCount to integer
DualMachineCount.vType = gp.GRB.INTEGER
model.update()

# Updating the integrality of SingleMachineCount to an integer variable
SingleMachineCount.vtype = gp.GRB.INTEGER

# No additional code needed since the variable "DualMachineCount" is already defined with non-negativity guaranteed by being a continuous variable in gurobipy.

# The variable "SingleMachineCount" already has a non-negative domain by default in Gurobi as it is declared as a continuous variable.
# No additional constraint is needed for this requirement.

# Add constraint for total stamping capacity
model.addConstr(DualMachineCount * DualCap + SingleMachineCount * SingleCap >= MinLetters, name="min_stamping_capacity")

# Add glue usage constraint
model.addConstr(DualMachineCount * DualGlue + SingleMachineCount * SingleGlue <= MaxGlue, name="glue_usage_constraint")

# Adding combined constraints for stamping capacity and glue consumption  
model.addConstr(DualMachineCount * DualCap + SingleMachineCount * SingleCap >= MinLetters, name="stamping_capacity")  
model.addConstr(DualMachineCount * DualGlue + SingleMachineCount * SingleGlue <= MaxGlue, name="glue_consumption")

# Add minimum letters constraint
model.addConstr(DualMachineCount * DualCap + SingleMachineCount * SingleCap >= MinLetters, name="min_letters")

# Add maximum glue constraint
model.addConstr(DualMachineCount * DualGlue + SingleMachineCount * SingleGlue <= MaxGlue, name="max_glue")

# Add glue consumption and stamping capacity constraints
model.addConstr(DualGlue * DualMachineCount + SingleGlue * SingleMachineCount <= MaxGlue, name="glue_consumption_limit")
model.addConstr(DualCap * DualMachineCount + SingleCap * SingleMachineCount >= MinLetters, name="stamping_capacity_requirement")

# Add glue and capacity constraints
model.addConstr(DualGlue * DualMachineCount + SingleGlue * SingleMachineCount <= MaxGlue, name="glue_constraint")
model.addConstr(DualCap * DualMachineCount + SingleCap * SingleMachineCount >= MinLetters, name="capacity_constraint")

# Add constraint to ensure the number of single model stamping machines is greater than the number of dual model stamping machines
model.addConstr(SingleMachineCount >= DualMachineCount + 1, name="machine_count_constraint")

# Add stamping capacity constraint
model.addConstr(DualCap * DualMachineCount + SingleCap * SingleMachineCount >= MinLetters, name="stamping_capacity")

# Add glue consumption constraint
model.addConstr(
    DualGlue * DualMachineCount + SingleGlue * SingleMachineCount <= MaxGlue, 
    name="glue_consumption_constraint"
)

# Set objective
model.setObjective(DualMachineCount + SingleMachineCount, gp.GRB.MINIMIZE)

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
