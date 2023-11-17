set Time;           # Time series

param eff_SOEC;     # Energy input/Hydrogen output
param eff_SOFC;		# Hydrogen input/Energy output
param V_max;        # The size of the tank
param P {Time};     # Electricity price at time t
param P_SOEC;       # The max power rate of SOEC
param P_SOFC;       # The max power rate of SOFC
param power_SOEC := 1 #MW 
param power_SOFC := 1 #MW

var x1 {Time} binary;      # x1 = 1 if SOEC uses the electricity 
						   # to produce the hydrogen gas, x1 = 0 if...
				   
var x2 {Time} binary;	   # x2 = 1 if SOFC uses the hydrogen gas 
						   # to produce the electricity, x2 = 0 if...				   

var E {Time};			   # The electricity energy at time t
var V {Time};		       # The hydrogen gas at time t	
var C {Time} >= 0;         # The cumulated gas in the tank

minimize Cost: V_max + sum{t in Time} P[t] * E[t];

subject to Transition_Hydrogen_Electricity1 {t in Time}: 
E[t] = x1[t] * V[t] / eff_SOEC + X2[t] * V[t] * eff_SOFC;

subject to Transition_Hydrogen_Electricity2 {t in Time}: 
V[t] = E[t] * x1[t] * eff_SOEC + X2[t] * E[t] / eff_SOFC;

subject to Working_Mode {t in Time}: 
x1[t] + x2[t] <= 1;

subject to restVolume_limit_1 {t in Time}:
V[t] >= -(1-x1[t]) * C[t];

subject to restVolume_limit_2 {t in Time}:
V[t] <= (1-x2[t]) * (V_max - C[t]);

subject to InitialCondition:
    C[0] = 0;

subject to CumulativeGas{t in Time}:
    C[t] = C[t-1] + V[t];

subject to VolumeConstraint{t in Time}:
    C[t] <= V_max;

subject to Powerlimit1 {t in Time}: 
	E[t] <= P_SOEC * power_SOEC;
	
subject to Powerlimit2 {t in Time}: 
	E[t] <= P_SOFC * power_SOFC;


