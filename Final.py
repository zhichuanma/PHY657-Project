from pulp import *
import pandas as pd

df = pd.read_csv(".//database//Monthly_data.csv")

# Define the time period
time_periods = df["Datetime (Local)"]

# Define parameters
eff_SOEC = 0.5
eff_SOFC = 0.5
V_max = 5
P_SOEC = 1
P_SOFC = 1 
Price = df['Price (EUR/MWhe)']

# Elementary features:

lp = LpProblem("Profit_making", LpMaximize)

# Define variables
x1 = {t: LpVariable(f"x1_{t}", cat="Binary") for t in time_periods}
x2 = {t: LpVariable(f"x2_{t}", cat="Binary") for t in time_periods}
E = {t: LpVariable(f"E_{t}", cat="Continuous") for t in time_periods}
V = {t: LpVariable(f"V_{t}", cat="Continuous") for t in time_periods}
C = {t: LpVariable(f"C_{t}", lowBound=0, cat="Continuous") for t in time_periods}

# Add the objective function
objective_function = V_max + sum(Price[t] * E[t] for t in time_periods)
lp += objective_function

# Add contraints
# Transition_hydrogen_electricity1_rule
for t in time_periods:
    lp += E[t] == x1[t] * V[t] / eff_SOEC + x2[t] * V[t] * eff_SOFC, f"transition_rule1_t{t}"

# Transition_hydrogen_electricity2_rule
for t in time_periods:
    lp += V[t] == E[t] * x1[t] * eff_SOEC + x2[t] * E[t] / eff_SOFC, f"transition_rule2_t{t}"

# Working mode rule
for t in time_periods:
    lp += x1[t] + x2[t] <= 1, f"working_mode_rule_t{t}"

# Rest_volume_limit_1_rule
for t in time_periods:
    lp += V[t] >= -(1 - x1[t]) * C[t], f"rest_volume_limit_1_rule_t{t}"

# Rest_volume_limit_2_rule
for t in time_periods:
    lp += V[t] <= (1 - x2[t]) * (V_max - C[t]), f"rest_volume_limit_2_rule_t{t}"

# Initial_condition_rule
lp += C[time_periods[0]] == 0, f"Initial_condition_rule_t{t}"

# Cumulative_gas_rule
for t in time_periods:
    if t == time_periods[0]:
        continue
    lp += C[t] == C[t-1] + V[t], f"Cumulative_gas_rule_t{t}"

# Volume_constraint_rule
for t in time_periods:
   lp += C[t] <= V_max, f"Volume_constraint_rule_t{t}"

# Power_limit1_rule
for t in time_periods:
   lp += E[t] <= P_SOEC, f"Power_limit1_rule_t{t}"

# Power_limit2_rule
for t in time_periods:
   lp += E[t] <= P_SOFC * eff_SOFC, f"Power_limit2_rule_t{t}"

# Solve the problem
lp.solve()
