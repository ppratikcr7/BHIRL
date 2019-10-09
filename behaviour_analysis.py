#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 17:14:53 2019

@author: archan
"""

# Importing libraries for plotting graphs from csv file
import matplotlib.pyplot as plt
import csv
x=[]
y=[]

# Logic to plot graph from our csv file

with open('output.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
        x.append(int(row[0]))
        y.append(int(row[1]))

plt.plot(x,y, 'ro')
plt.xlabel ('Time')
plt.ylabel ('Car Distance')
plt.title('Behavourial Analysis')
plt.savefig('results.png', dpi=100)
plt.show()

# Graph will be saved in results.png file
