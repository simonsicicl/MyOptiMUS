import json
import numpy as np
import math

import gurobipy as gp

# Define model
model = gp.Model('model')

with open("data/nl4opt/prob_207/data.json", "r") as f:
    data = json.load(f)

TimePrintingGraph = data["TimePrintingGraph"] # scalar parameter
TimeScanningGraph = data["TimeScanningGraph"] # scalar parameter
TimePrintingMusic = data["TimePrintingMusic"] # scalar parameter
TimeScanningMusic = data["TimeScanningMusic"] # scalar parameter
MaxTimePrinting = data["MaxTimePrinting"] # scalar parameter
MaxTimeScanning = data["MaxTimeScanning"] # scalar parameter
ProfitGraph = data["ProfitGraph"] # scalar parameter
ProfitMusic = data["ProfitMusic"] # scalar parameter
NumberGraphPaper = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberGraphPaper")
NumberMusicPaper = model.addVar(vtype=gp.GRB.CONTINUOUS, name="NumberMusicPaper")

# Ensure the number of reams of graph paper produced is non-negative
model.addConstr(NumberGraphPaper >= 0, name="non_negative_graph_paper")

# No additional code is necessary as the non-negativity constraint is automatically handled
# by defining the variable `NumberMusicPaper` as a continuous variable in Gurobi.

# Add constraint for printing machine time usage
model.addConstr(
    NumberGraphPaper * TimePrintingGraph + NumberMusicPaper * TimePrintingMusic <= MaxTimePrinting,
    name="printing_time_limit"
)

# Add constraint to limit total scanning time
model.addConstr(
    NumberGraphPaper * TimeScanningGraph + NumberMusicPaper * TimeScanningMusic <= MaxTimeScanning,
    name="scanning_time_limit"
)

# Add constraint on the time usage of the printing machine
model.addConstr(
    NumberGraphPaper * TimePrintingGraph + NumberMusicPaper * TimePrintingMusic <= MaxTimePrinting,
    name="time_usage_constraint"
)

# Add constraint on the time usage of the scanning machine
model.addConstr(
    NumberGraphPaper * TimeScanningGraph + NumberMusicPaper * TimeScanningMusic <= MaxTimeScanning,
    name="scanning_time_constraint"
)

# Set objective
model.setObjective(ProfitGraph * NumberGraphPaper + ProfitMusic * NumberMusicPaper, gp.GRB.MAXIMIZE)

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
