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
NumRegularGlassPanes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumRegularGlassPanes")
NumTemperedGlassPanes = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumTemperedGlassPanes")

# Change the variable type to integer to ensure NumRegularGlassPanes is an integer
NumRegularGlassPanes.vtype = gp.GRB.INTEGER

# Change the variable NumTemperedGlassPanes to be integral
NumTemperedGlassPanes.vtype = gp.GRB.INTEGER

# Add non-negativity constraint for NumRegularGlassPanes
model.addConstr(NumRegularGlassPanes >= 0, name="non_negativity_RegularGlassPanes")

# Add constraint to ensure NumTemperedGlassPanes is non-negative
model.addConstr(NumTemperedGlassPanes >= 0, name="non_negative_NumTemperedGlassPanes")

# Add constraint to limit total heating time for regular glass panes
model.addConstr(NumRegularGlassPanes * TimeRegHeat <= MaxTime, name="time_limit_regular_glass")

# Add total cooling machine time usage constraint
model.addConstr(NumRegularGlassPanes * TimeRegCool <= MaxTime, name="cooling_machine_time_limit")

# Add constraint to ensure the total time used in the heating machine does not exceed MaxTime
model.addConstr(TimeTempHeat * NumTemperedGlassPanes <= MaxTime, name="time_limit_heating_machine")

# Add constraint to limit total time used in the cooling machine by tempered glass panes
model.addConstr(NumTemperedGlassPanes * TimeTempCool <= MaxTime, name="cooling_time_limit")

# Add constraints for heating and cooling machine time limits
model.addConstr(
    TimeRegHeat * NumRegularGlassPanes + TimeTempHeat * NumTemperedGlassPanes <= MaxTime, 
    name="HeatingMachineTimeLimit"
)
model.addConstr(
    TimeRegCool * NumRegularGlassPanes + TimeTempCool * NumTemperedGlassPanes <= MaxTime, 
    name="CoolingMachineTimeLimit"
)

# Add time constraints for heating and cooling machines
model.addConstr(
    TimeRegCool * NumRegularGlassPanes + TimeTempCool * NumTemperedGlassPanes <= MaxTime, 
    name="CoolingTimeConstraint"
)
model.addConstr(
    TimeRegHeat * NumRegularGlassPanes + TimeTempHeat * NumTemperedGlassPanes <= MaxTime, 
    name="HeatingTimeConstraint"
)

# Add time constraints for heating and cooling machines:

# Heating time constraint
model.addConstr(
    (NumRegularGlassPanes * TimeRegHeat) + (NumTemperedGlassPanes * TimeTempHeat) <= MaxTime,
    name="heating_time_constraint"
)

# Cooling time constraint
model.addConstr(
    (NumRegularGlassPanes * TimeRegCool) + (NumTemperedGlassPanes * TimeTempCool) <= MaxTime,
    name="cooling_time_constraint"
)

# Add constraint to ensure total heating and cooling time does not exceed maximum daily usage time
model.addConstr(
    TimeRegHeat * NumRegularGlassPanes +
    TimeRegCool * NumRegularGlassPanes +
    TimeTempHeat * NumTemperedGlassPanes +
    TimeTempCool * NumTemperedGlassPanes <= MaxTime,
    name="machine_usage_time"
)

# Add total heating time constraint
model.addConstr(
    TimeRegHeat * NumRegularGlassPanes + TimeTempHeat * NumTemperedGlassPanes <= MaxTime,
    name="total_heating_time_constraint"
)

# Add total cooling time constraint
model.addConstr(
    TimeRegCool * NumRegularGlassPanes + TimeTempCool * NumTemperedGlassPanes <= MaxTime,
    name="total_cooling_time_constraint"
)

# Set objective
model.setObjective(
    ProfitReg * NumRegularGlassPanes + ProfitTemp * NumTemperedGlassPanes, 
    gp.GRB.MAXIMIZE
)

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
