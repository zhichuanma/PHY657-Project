from pulp import *
import pandas as pd

df = pd.read_csv(".//database//Monthly_data.csv")

# Define the time period
time_periods = df["Datetime (Local)"]

# Define parameters
'''
The eff_SOEC's and eff_SOFC'S units are both kWh/m^3
it means the quantity of electricity energy input in a return of 1 m^3 hydrogen gas,
taking into consideration of the efficiency
the desity of hydrogen: 0.08 kg/m^3
transfer efficiency: 90%
'''
eff_SOEC = 39.82 * 0.08 * 0.9 #39.82's unit is kWh/kg
eff_SOFC = 27 * 0.08 * 0.9 # 27's unit is kWh/kg
#eff_SOEC =  1
#eff_SOFC =  2
V_max = 5
P_SOEC = 1
P_SOFC = 1 
Price = df['Price (EUR/MWhe)']
M = 1000
# Elementary features:

lp = LpProblem("Profit_making", LpMaximize)

# Define variables
x1 = {t: LpVariable(f"x1_{t}", cat="Binary") for t in time_periods}
x2 = {t: LpVariable(f"x2_{t}", cat="Binary") for t in time_periods}
z1 = {t: LpVariable(f"z1_{t}",lowBound=0, cat="Continuous") for t in time_periods}
z2 = {t: LpVariable(f"z2_{t}",lowBound=0, cat="Continuous") for t in time_periods}
w1 = {t: LpVariable(f"w1_{t}",lowBound=0, cat="Continuous") for t in time_periods}
w2 = {t: LpVariable(f"w2_{t}",lowBound=0, cat="Continuous") for t in time_periods}
E = {t: LpVariable(f"E_{t}", cat="Continuous") for t in time_periods}
V = {t: LpVariable(f"V_{t}", cat="Continuous") for t in time_periods}
C = {t: LpVariable(f"C_{t}", lowBound=0, cat="Continuous") for t in time_periods}

# Add the objective function
objective_function = 287.93 * V_max * 1.3 + sum(Price[t] * E[t] for t in time_periods)
lp += objective_function

# Add constraints

for t in time_periods:
    lp += z1[t] <= M * x1[t]  # z1[t] is 0 when x1[t] is 0
    lp += z1[t] <= V[t]      # z1[t] can be at most V[t]
    lp += z1[t] >= V[t] - M * (1 - x1[t])  # Forces z1[t] to V[t] when z1[t] is 1

    lp += z2[t] <= M * x2[t]  # Similar constraints for z2[t]
    lp += z2[t] <= V[t]
    lp += z2[t] >= V[t] - M * (1 - x2[t])

# Transition_hydrogen_electricity1_rule
for t in time_periods:
    lp += E[t] == z1[t] * (1 / eff_SOEC) + z2[t] * eff_SOFC, f"transition_rule1_t{t}"

# Transition_hydrogen_electricity2_rule
for t in time_periods:
    lp += V[t] == z1[t] * eff_SOEC + z2[t] * (1 / eff_SOFC), f"transition_rule2_t{t}"

# Working mode rule
for t in time_periods:
    lp += x1[t] + x2[t] <= 1, f"working_mode_rule_t{t}"

for t in time_periods:
    lp += w1[t] >= C[t] - M * x1[t]  # w1[t] is at least C[t] when x1[t] is 0
    lp += w1[t] <= M * (1 - x1[t])   # w1[t] is 0 when x1[t] is 1

# Rest_volume_limit_1_rule
for t in time_periods:
    lp += V[t] >= -w1[t], f"rest_volume_limit_1_rule_t{t}"

for t in time_periods:
    lp += w2[t] >= (V_max - C[t]) - M * x2[t]  # W2[t] is at least V_max - C[t] when x2[t] is 0
    lp += w2[t] <= M * (1 - x2[t])             # W2[t] is 0 when x2[t] is 1

# Rest_volume_limit_2_rule
for t in time_periods:
    lp += V[t] <= w2[t], f"rest_volume_limit_2_rule_t{t}"

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
