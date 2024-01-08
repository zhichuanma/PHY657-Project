from pyomo.environ import *
import pandas as pd

df = pd.read_csv(".//database//Weekly_data.csv")
time_periods = df["Datetime (Local)"].tolist()
price_dict = df['Price (EUR/MWhe)'].to_dict()

# Create a model
model = ConcreteModel()

# Sets
model.T = Set(initialize=time_periods)

# Parameters
model.eff_SOEC = Param(initialize=39.82 * 0.08 * 0.9 * 0.001)
model.eff_SOFC = Param(initialize=27 * 0.08 * 0.9 * 0.001)
model.V_max = Param(initialize=5)
model.P_SOEC = Param(initialize=1)
model.P_SOFC = Param(initialize=1)
model.Price = Param(model.T, initialize=price_dict)  # Assuming price_dict is a dictionary of prices

# Variables
model.x1 = Var(model.T, within=Binary)
model.x2 = Var(model.T, within=Binary)
model.z1 = Var(model.T, within=NonNegativeReals)
model.z2 = Var(model.T, within=NonNegativeReals)
model.E_in = Var(model.T, within=NonNegativeReals)
model.E_out = Var(model.T, within=NonNegativeReals)
model.V = Var(model.T, within=Reals)
model.C = Var(model.T, within=NonNegativeReals)

# Objective
def objective_rule(model):
    return - model.V_max * 287.93 * 1.3 - sum(model.Price[t] * (model.E_in[t] - model.E_out[t]) for t in model.T)
model.Profit = Objective(rule=objective_rule, sense=maximize)

# Constraints
def transition_rule1(model, t):
    return model.E_in[t] == model.z1[t] / model.eff_SOEC
model.Transition1 = Constraint(model.T, rule=transition_rule1)

# Add other constraints similarly...
def transition_rule2(model, t):
    return model.E_out[t] == model.z2[t] * model.eff_SOFC
model.Transition2 = Constraint(model.T, rule=transition_rule2)

def working_mode_rule(model, t):
    return model.x1[t] + model.x2[t] <= 1
model.Working_Mode = Constraint(model.T, rule=working_mode_rule)

def Initial_condition_rule(model):
    return model.C[time_periods[0]] == 0
model.initial_condition = Constraint(rule=Initial_condition_rule)

def Cumulative_gas_rule(model, t):
    if t == time_periods[0]:
        return model.C[0] == 0
    return model.C[t] == model.C[t-1] + model.V[t-1]
model.cumulative_gas_rule = Constraint(model.T, rule=Cumulative_gas_rule)

def volume_balance(model, t):
    return model.V[t] == model.z1[t] + model.z2[t]
model.volume_balance_rule = Constraint(model.T, rule=volume_balance)

def Power_limit1_rule(model, t):
    return model.E_in[t] <= model.P_SOEC * model.x1[t]
model.power_limit1_rule = Constraint(model.T, rule=Power_limit1_rule)

def Power_limit2_rule(model, t):
    return model.E_out[t] <= model.P_SOFC * model.x2[t]
model.power_limit2_rule = Constraint(model.T, rule=Power_limit2_rule)

# Solving the model
solver = SolverFactory('ipopt')  # Or another solver as per your problem's requirement
solver.solve(model)

# Access the solution
for t in model.T:
    print(f"Time {t}: E={model.E_out[t].value}, V={model.V[t].value}, C={model.C[t].value}")
