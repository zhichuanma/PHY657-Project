from pyomo.environ import *
import pandas as pd
Price_data = pd.read_csv(".//database//Yearly_data.csv")
#print(Price_data['Price (EUR/MWhe)'])

# Define the model
model = ConcreteModel()

# Sets
model.Time = Set()

# Define the model
model = ConcreteModel()

# Sets
model.Time = Set(initialize=Price_data['Datetime (Local)'])  # Example Time set, you need to define this properly based on your problem

# Parameters with specified values
model.eff_SOEC = Param(initialize=0.5)
model.eff_SOFC = Param(initialize=0.5)
model.V_max = Param(initialize=5)
model.P_SOEC = Param(initialize=1)
model.P_SOFC = Param(initialize=1)

# Assuming Price is a parameter that will be provided externally,
# it's initialized here with some dummy values for demonstration
model.Price = Param(model.Time, initialize=Price_data['Price (EUR/MWhe)'])

# Variables
model.x1 = Var(model.Time, within=Binary)
model.x2 = Var(model.Time, within=Binary)
model.E = Var(model.Time)
model.V = Var(model.Time)
model.C = Var(model.Time, within=NonNegativeReals)

# Objective
def objective_rule(model):
    return model.V_max + sum(model.Price[t] * model.E[t] for t in model.Time)
model.Cost = Objective(rule=objective_rule, sense=minimize)

# Constraints
def transition_hydrogen_electricity1_rule(model, t):
    return model.E[t] == model.x1[t] * model.V[t] / model.eff_SOEC + model.x2[t] * model.V[t] * model.eff_SOFC
model.Transition_Hydrogen_Electricity1 = Constraint(model.Time, rule=transition_hydrogen_electricity1_rule)

def transition_hydrogen_electricity2_rule(model, t):
    return model.V[t] == model.E[t] * model.x1[t] * model.eff_SOEC + model.x2[t] * model.E[t] / model.eff_SOFC
model.Transition_Hydrogen_Electricity2 = Constraint(model.Time, rule=transition_hydrogen_electricity2_rule)

def working_mode_rule(model, t):
    return model.x1[t] + model.x2[t] <= 1
model.Working_Mode = Constraint(model.Time, rule=working_mode_rule)

def rest_volume_limit_1_rule(model, t):
    return model.V[t] >= -(1 - model.x1[t]) * model.C[t]
model.RestVolume_Limit_1 = Constraint(model.Time, rule=rest_volume_limit_1_rule)

def rest_volume_limit_2_rule(model, t):
    return model.V[t] <= (1 - model.x2[t]) * (model.V_max - model.C[t])
model.RestVolume_Limit_2 = Constraint(model.Time, rule=rest_volume_limit_2_rule)

def initial_condition_rule(model):
    return model.C[model.Time.first()] == 0
model.InitialCondition = Constraint(rule=initial_condition_rule)

def cumulative_gas_rule(model, t):
    if t == model.Time.first():
        return Constraint.Skip
    return model.C[t] == model.C[t-1] + model.V[t]
model.CumulativeGas = Constraint(model.Time, rule=cumulative_gas_rule)

def volume_constraint_rule(model, t):
    return model.C[t] <= model.V_max
model.VolumeConstraint = Constraint(model.Time, rule=volume_constraint_rule)

def power_limit1_rule(model, t):
    return model.E[t] <= model.P_SOEC
model.Powerlimit1 = Constraint(model.Time, rule=power_limit1_rule)

def power_limit2_rule(model, t):
    return model.E[t] <= model.P_SOFC * model.eff_SOFC
model.Powerlimit2 = Constraint(model.Time, rule=power_limit2_rule)


def Initial_value(model):
    return model.E[t] <= model.P_SOFC * model.eff_SOFC
model.Powerlimit2 = Constraint(model.Time, rule=power_limit2_rule)

# Assuming you have defined and solved your model as shown previously
solver = SolverFactory('IPOPT')  # Replace 'glpk' with the solver you are using
results = solver.solve(model, tee=True)

# Check if the solution is optimal
if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
    # Print the values of the variables
    for t in model.Time:
        print(f"Time {t}:")
        print(f"  x1 = {model.x1[t].value}")
        print(f"  x2 = {model.x2[t].value}")
        print(f"  E = {model.E[t].value}")
        print(f"  V = {model.V[t].value}")
        print(f"  C = {model.C[t].value}")
else:
    print("No optimal solution found.")

import matplotlib.pyplot as plt
import re

# Assuming 'solver_log.txt' is a file that contains the solver's iteration log
# with lines that include the iteration number and corresponding objective value.
log_file = 'solver_log.txt'

# Initialize lists to hold iteration numbers and objective function values
iterations = []
objective_values = []

# Regex pattern to match lines in the log file
# This will need to be adjusted based on the actual format of your log file.
pattern = re.compile(r'Iteration (\d+):.+Objective value: ([\d\.]+)')

# Read the log file and extract iteration and objective function values
with open(log_file, 'r') as file:
    for line in file:
        match = pattern.search(line)
        if match:
            iter_num = int(match.group(1))
            obj_val = float(match.group(2))
            iterations.append(iter_num)
            objective_values.append(obj_val)

# Plotting the objective function values against iteration values
plt.plot(iterations, objective_values, marker='o')
plt.xlabel('Iteration')
plt.ylabel('Objective Function Value')
plt.title('Objective Function Value vs Iteration')
plt.grid(True)
plt.show()
