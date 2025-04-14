import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_242/data.json", "r") as f:
    data = json.load(f)

CaloriesSalmon = data["CaloriesSalmon"] # scalar parameter
ProteinSalmon = data["ProteinSalmon"] # scalar parameter
SodiumSalmon = data["SodiumSalmon"] # scalar parameter
CaloriesEggs = data["CaloriesEggs"] # scalar parameter
ProteinEggs = data["ProteinEggs"] # scalar parameter
SodiumEggs = data["SodiumEggs"] # scalar parameter
MaxEggProportion = data["MaxEggProportion"] # scalar parameter
MinTotalCalories = data["MinTotalCalories"] # scalar parameter
MinTotalProtein = data["MinTotalProtein"] # scalar parameter
NumberSalmonMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberSalmonMeals")
NumberEggMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberEggMeals")
TotalMeals = model.addVar(vtype=gp.GRB.CONTINUOUS, name="TotalMeals")

# No additional code needed since the variable "NumberSalmonMeals" is defined with non-negativity by default through its lower bound of 0 in Gurobi.

# Variable 'NumberEggMeals' is already non-negative due to its default domain in Gurobi (continuous domain variables are non-negative by default unless specified otherwise).

# Adding the constraint to ensure at most MaxEggProportion of meals can be eggs
model.addConstr(NumberEggMeals <= MaxEggProportion * TotalMeals, name="max_egg_meal_proportion")

# Add total caloric intake constraint
model.addConstr(
    CaloriesSalmon * NumberSalmonMeals + CaloriesEggs * NumberEggMeals >= MinTotalCalories,
    name="total_caloric_intake"
)

# Add a constraint to ensure total protein intake is at least MinTotalProtein
model.addConstr(
    ProteinSalmon * NumberSalmonMeals + ProteinEggs * NumberEggMeals >= MinTotalProtein,
    name="protein_intake_constraint"
)

# Add constraint: TotalMeals equals the sum of salmon and egg meals
model.addConstr(TotalMeals == NumberSalmonMeals + NumberEggMeals, name="TotalMeals_calculation")

# Add constraint to ensure the minimum caloric requirement is met
model.addConstr(
    NumberSalmonMeals * CaloriesSalmon + NumberEggMeals * CaloriesEggs >= MinTotalCalories,
    name="min_caloric_requirement"
)

# Add constraint to ensure the minimum protein requirement is met
model.addConstr(
    NumberSalmonMeals * ProteinSalmon + NumberEggMeals * ProteinEggs >= MinTotalProtein, 
    name="min_protein_requirement"
)

# Add constraint to ensure the proportion of egg meals is within the maximum allowable limit
model.addConstr(NumberEggMeals <= MaxEggProportion * (NumberSalmonMeals + NumberEggMeals), name="max_egg_proportion")

# Set objective
model.setObjective(NumberSalmonMeals * SodiumSalmon + NumberEggMeals * SodiumEggs, gp.GRB.MINIMIZE)

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
