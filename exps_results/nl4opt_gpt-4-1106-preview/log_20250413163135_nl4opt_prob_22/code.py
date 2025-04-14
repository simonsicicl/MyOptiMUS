import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_22/data.json", "r") as f:
    data = json.load(f)

MaxTime = data["MaxTime"] # scalar parameter
TimeRegHeat = data["TimeRegHeat"] # scalar parameter
TimeRegCool = data["TimeRegCool"] # scalar parameter
TimeTempHeat = data["TimeTempHeat"] # scalar parameter
TimeTempCool = data["TimeTempCool"] # scalar parameter
ProfitReg = data["ProfitReg"] # scalar parameter
ProfitTemp = data["ProfitTemp"] # scalar parameter
NumberOfRegularGlassPanes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfRegularGlassPanes")
NumberOfTemperedGlassPanes = model.addVar(vtype=gp.GRB.INTEGER, name="NumberOfTemperedGlassPanes")

# No code needed because the variable NumberOfRegularGlassPanes is already defined as an integer in the provided code snippet.

# Since NumberOfTemperedGlassPanes is already defined as an integer variable, no additional code is needed for this constraint.

model.addConstr(NumberOfRegularGlassPanes >= 0, name="non_negativity_regular_glass")

# Non-negativity constraint for the number of tempered glass panes
model.addConstr(NumberOfTemperedGlassPanes >= 0, name="nonnegativity_constraint")

# Add constraint for maximum time used in heating machine by regular glass panes
model.addConstr(NumberOfRegularGlassPanes * TimeRegHeat <= MaxTime, name="max_heating_time_regular_glass")

# Add constraint for total cooling time for regular glass panes
model.addConstr(NumberOfRegularGlassPanes * TimeRegCool <= MaxTime, name="total_cooling_time_constraint")

# Total time used constraint for heating machine by tempered glass panes
model.addConstr(NumberOfTemperedGlassPanes * TimeTempHeat <= MaxTime, name="total_heating_time_constraint")

# Total cooling time for tempered glass panes must not exceed MaxTime minutes per day
model.addConstr(NumberOfTemperedGlassPanes * TimeTempCool <= MaxTime, name="total_cooling_time_constraint")

# Total time used for heating constraint
model.addConstr(NumberOfRegularGlassPanes * TimeRegHeat <= MaxTime, "heating_time_limit")

# Add constraint for cooling time of regular glass panes
model.addConstr(NumberOfRegularGlassPanes * TimeRegCool <= MaxTime, name="cooling_time_regular_glass_panes")

# Add time constraint for heating machines
model.addConstr(NumberOfRegularGlassPanes * TimeRegHeat + NumberOfTemperedGlassPanes * TimeTempHeat <= MaxTime, name="max_heating_time")

# Cooling time constraint for all glass panes
cooling_time_constraint = TimeRegCool * NumberOfRegularGlassPanes + TimeTempCool * NumberOfTemperedGlassPanes <= MaxTime
model.addConstr(cooling_time_constraint, name="cooling_time_constraint")

# Define objective function
model.setObjective(ProfitReg * NumberOfRegularGlassPanes + ProfitTemp * NumberOfTemperedGlassPanes, gp.GRB.MAXIMIZE)

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
