import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nlp4lp/16/data.json", "r") as f:
    data = json.load(f)

N = data["N"] # scalar parameter
AssemblyHour = np.array(data["AssemblyHour"]) # ['N']
TestingHour = np.array(data["TestingHour"]) # ['N']
MaterialCost = np.array(data["MaterialCost"]) # ['N']
MaxAssembly = data["MaxAssembly"] # scalar parameter
MaxTesting = data["MaxTesting"] # scalar parameter
Price = np.array(data["Price"]) # ['N']
MaxOvertimeAssembly = data["MaxOvertimeAssembly"] # scalar parameter
OvertimeAssemblyCost = data["OvertimeAssemblyCost"] # scalar parameter
MaterialDiscount = data["MaterialDiscount"] # scalar parameter
DiscountThreshold = data["DiscountThreshold"] # scalar parameter
ProductionQuantity = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name="ProductionQuantity")
OvertimeHoursUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OvertimeHoursUsed")
ExcessAssemblyHours = model.addVar(vtype=gp.GRB.CONTINUOUS, name="ExcessAssemblyHours")
TotalMaterialDiscount = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMaterialDiscount")

N = len(AssemblyHour)
ProductionQuantity = model.addVars(N, vtype=gp.GRB.CONTINUOUS, name='ProductionQuantity')

# Add constraint for total testing hours not exceeding maximum available testing hours
testing_hours_expr = gp.quicksum(ProductionQuantity[i] * TestingHour[i] for i in range(N))
model.addConstr(testing_hours_expr <= MaxTesting, name="max_testing_hours")

# Add non-negativity constraints for production quantities
for i in range(N):
    model.addConstr(ProductionQuantity[i] >= 0, name=f"non_negativity_{i}")

# Ensure that the total overtime assembly hours do not exceed the maximum overtime assembly hours available
OvertimeHoursUsed = model.addVar(vtype=gp.GRB.CONTINUOUS, name="OvertimeHoursUsed")
model.addConstr((gp.quicksum(ProductionQuantity[i] * AssemblyHour[i] for i in range(N)) - MaxAssembly) <= OvertimeHoursUsed, name="calc_overtime_hours_used")
model.addConstr(OvertimeHoursUsed <= MaxOvertimeAssembly, name="max_overtime_assembly")

# Constraint: Excess assembly hours must be greater than or equal to the difference between total assembly hours and the maximum assembly hours, if positive
total_assembly_hours_expr = gp.quicksum(AssemblyHour[i] * ProductionQuantity[i] for i in range(N))
model.addConstr(ExcessAssemblyHours >= total_assembly_hours_expr - MaxAssembly, name="excess_assembly_hours")

# Excess assembly hours must be non-negative
model.addConstr(ExcessAssemblyHours >= 0, name="excess_assembly_non_negative")

# Fixing the code

# Add TotalMaterialDiscount constraint
discount_vars = model.addVars(N, vtype=gp.GRB.BINARY, name='DiscountVar')
for i in range(N):
    # Add constraint that turns discount_vars[i] to 1 if ProductionQuantity[i] reaches the threshold
    model.addGenConstrIndicator(discount_vars[i], True, ProductionQuantity[i] - DiscountThreshold, gp.GRB.GREATER_EQUAL, 0)
TotalMaterialDiscount_expr = gp.quicksum(
    MaterialCost[i] * ProductionQuantity[i] * (1 - MaterialDiscount * discount_vars[i])
    for i in range(N)
)
model.addConstr(TotalMaterialDiscount == TotalMaterialDiscount_expr, name='total_material_discount')

# Constraint: Overtime hours used must not exceed the maximum overtime hours available for assembly
model.addConstr(OvertimeHoursUsed <= MaxOvertimeAssembly, name="overtime_assembly_limit")

# Set objective
objective = gp.quicksum(Price[i] * ProductionQuantity[i] for i in range(N)) - gp.quicksum(MaterialCost[i] * ProductionQuantity[i] for i in range(N)) - OvertimeHoursUsed * OvertimeAssemblyCost + TotalMaterialDiscount
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
