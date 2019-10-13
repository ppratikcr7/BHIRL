import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import re
import csv
import numpy as np

#Reading csv for data stored by Demo GUI:
with open('data_dynamic.csv', 'r') as f:
    reader = csv.reader(f)
    table_data = list(reader)

# Initialize a figure with ff.create_table(table_data)
fig = ff.create_table(table_data, height_constant=60)

# Fetch data to plot Epochs Vs Accuracy:
df = pd.read_csv("data_dynamic.csv")
epoch_list = []
for i, row in enumerate(df["Epochs"]):
    if(row == "_"):
        pass
    else:
        epoch_list.append(int(row))

max_epoch = max(epoch_list)
epochs = np.arange(max_epoch+1)
red_acc = ['0']
yellow_acc = ['0']
brown_acc = ['0']
crash_acc = ['0']
y_r_acc = ['0']

for i, row in enumerate(df["Name"]):
    if(row == "red"):
        red_acc.append(df["Accuracy"][i])
    elif(row == "yellow"):
        yellow_acc.append(df["Accuracy"][i])
    elif(row == "brown"):
        brown_acc.append(df["Accuracy"][i])
    elif(row == "bumping"):
        crash_acc.append(df["Accuracy"][i])
    elif(row == "yellow_red"):
        y_r_acc.append(df["Accuracy"][i])

#Generating traces of plots for all skills:
trace1 = go.Scatter(x=epochs, y=red_acc,
                    marker=dict(color='#FF0000'),
                    name= 'Red Skill',
                    xaxis='x2', yaxis='y2')
trace2 = go.Scatter(x=epochs, y=yellow_acc,
                    marker=dict(color='#FFFF00'),
                    name= 'Yellow Skill',
                    xaxis='x2', yaxis='y2')

trace3 = go.Scatter(x=epochs, y=brown_acc,
                    marker=dict(color='#654321'),
                    name= 'Brown Skill',
                    xaxis='x2', yaxis='y2')

trace4 = go.Scatter(x=epochs, y=crash_acc,
                    marker=dict(color='#008000'),
                    name= 'Crash Skill',
                    xaxis='x2', yaxis='y2')
trace5 = go.Scatter(x=epochs, y=y_r_acc,
                    marker=dict(color='#0000FF'),
                    name= 'Yellow_Red Skill',
                    xaxis='x2', yaxis='y2')
# Add trace data to figure
fig.add_traces([trace1, trace2, trace3, trace4, trace5])

# initialize xaxis2 and yaxis2
fig['layout']['xaxis2'] = {}
fig['layout']['yaxis2'] = {}

# Edit layout for subplots
fig.layout.yaxis.update({'domain': [0, .5]})
fig.layout.yaxis2.update({'domain': [.6, 1]})

# The graph's yaxis2 MUST BE anchored to the graph's xaxis2 and vice versa
fig.layout.yaxis2.update({'anchor': 'x2'})
fig.layout.xaxis2.update({'anchor': 'y2'})
fig.layout.yaxis2.update({'title': 'Accuracy'})
fig.layout.xaxis2.update({'title': 'Epochs'})

# Update the margins to add a title and see graph x-labels.
fig.layout.margin.update({'t':25, 'l':25})
fig.layout.update({'title': 'Learning Efficiency'})

# Update the height because adding a graph vertically will interact with
# the plot height calculated for the table
fig.layout.update({'height':800})

# Plot!
fig.show()