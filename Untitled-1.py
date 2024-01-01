import numpy as np
x_set = [(1,4), (3,1), (3,3), (4,5), (5,3), (6,5)]
y_set = []

for i in range(1,7):
    for j in range(1,7):
        if (i,j) not in x_set:
            y_set.append((i,j))
print(np.random(0,1))
#for temp in range(0,6):

#print(y_set)