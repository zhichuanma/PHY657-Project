from pulp import *
import pandas as pd

df = pd.read_csv(".//database//Weekly_data.csv")

# Define the time period
time_periods = df["Datetime (Local)"]

# Define parameters
'''
The eff_SOEC's and eff_SOFC'S units are both MWh/m^3
it means the quantity of electricity energy input in a return of 1 m^3 hydrogen gas,
taking into consideration of the efficiency
the desity of hydrogen: 0.08 kg/m^3
transfer efficiency: 90%
'''
eff_SOEC = 39.82 * 0.08 * 0.9 * 0.001 #39.82's unit is kWh/kg
eff_SOFC = 27 * 0.08 * 0.9 * 0.001 # 27's unit is kWh/kg

V_max = 50000
P_SOEC = 1
P_SOFC = 1 
Price = df['Price (EUR/MWhe)']
M = 1000
# Elementary features:

lp = LpProblem("Profit_making", LpMinimize)

# Define variables
x1 = {t: LpVariable(f"x1_{t}", cat="Binary") for t in time_periods}
x2 = {t: LpVariable(f"x2_{t}", cat="Binary") for t in time_periods}
z1 = {t: LpVariable(f"z1_{t}",lowBound=0, cat="Continuous") for t in time_periods}
z2 = {t: LpVariable(f"z2_{t}",lowBound=0, cat="Continuous") for t in time_periods}
V = {t: LpVariable(f"V_{t}",lowBound=0, cat="Continuous") for t in time_periods}
E_in = {t: LpVariable(f"E_in_{t}",lowBound=1, cat="Continuous") for t in time_periods}
E_out = {t: LpVariable(f"E_out_{t}",lowBound=1, cat="Continuous") for t in time_periods}
C = {t: LpVariable(f"C_{t}", lowBound=0, cat="Continuous") for t in time_periods}

# Add the objective function
# objective_function = 287.93 * V_max * 1.3 #+ sum(Price[t] * (E_in[t] - E_out[t]) for t in time_periods)
lp += 287.93 * V_max * 1.3 + sum(Price[t] * (E_in[t] - E_out[t]) for t in time_periods)

# # Add constraints
# for t in time_periods:
#     lp += z1[t] <= x1[t] * M
#     lp += z2[t] >= - x2[t] * M
#     lp += V[t] == z1[t] + z2[t]


# Transition_hydrogen_electricity1_rule
for t in time_periods:
    lp += E_in[t] == z1[t] * (1 / eff_SOEC), f"transition_rule1_t{t}"

for t in time_periods:
    lp += E_out[t] == z2[t] * eff_SOFC, f"transition_rule2_t{t}"
# Transition_hydrogen_electricity2_rule
#for t in time_periods:
#    lp += V[t] == z1[t] * eff_SOEC + z2[t] * (1 / eff_SOFC), f"transition_rule2_t{t}"

# Working mode rule
for t in time_periods:
    lp += x1[t] + x2[t] <= 1, f"working_mode_rule_t{t}"

# for t in time_periods:
#     if t == time_periods[0]:  # Skip the first time period if initial C[t-1] is not defined
#         continue
#     # Constraint for when x1[t] is 1 and x2[t] is 0
#     lp += V[t] <= (V_max - C[t-1]) + M * (1 - x1[t]), f"V_leq_Vmax_minus_C_when_x1_1_t{t}"
#     # Constraint for when x1[t] is 0 and x2[t] is 1
#     lp += V[t] >= -C[t-1] - M *(1 - x2[t]), f"V_ge_minus_C_when_x2_1_t{t}"


# Initial_condition_rule
lp += C[time_periods[0]] == 0, f"Initial_condition_rule_t{t}"

# Cumulative_gas_rule
for t in time_periods:
    if t == time_periods[0]:
        continue
    lp += C[t] == C[t-1] + V[t-1], f"Cumulative_gas_rule_t{t}"

for t in time_periods:
   lp += V[t] == z1[t] - z2[t]

# Volume_constraint_rule
for t in time_periods:
   lp += C[t] <= V_max, f"Volume_constraint_rule_t{t}"

# Power_limit1_rule
for t in time_periods:
   lp += E_in[t] <= P_SOEC * x1[t], f"Power_limit1_rule_t{t}"

# Power_limit2_rule
for t in time_periods:
   lp += E_out[t] <= P_SOFC * x2[t], f"Power_limit2_rule_t{t}"


# Set a time limit
solver = PULP_CBC_CMD(timeLimit=1800)

# Solve the problem
lp.solve(solver)

x1_values = {t: pulp.value(x1[t]) for t in time_periods}
x2_values = {t: pulp.value(x2[t]) for t in time_periods}
C_values = {t: pulp.value(C[t]) for t in time_periods}
V_values = {t: pulp.value(V[t]) for t in time_periods}
E_in_values = {t: pulp.value(E_in[t]) for t in time_periods}
E_out_values = {t: pulp.value(E_out[t]) for t in time_periods}

Price_values = {t: pulp.value(Price[t]) for t in time_periods}

z1_values = {t: pulp.value(z1[t]) for t in time_periods}
z2_values = {t: pulp.value(z2[t]) for t in time_periods}

# print("Value of x1:", x1_values)
# print("Value of x2:", x2_values)

print("Value of z1:", z1_values)
print("Value of z2:", z2_values)

print("Value of C:", C_values)
print("Value of V:", V_values)

#print("Value of price:", Price_values)
print("Value of E_in:", E_in_values)
print("Value of E_out:", E_out_values)