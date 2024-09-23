import os

import plotly.graph_objects as go
import pandas as pd
import numpy as np

############################################################################################
# To gain insight into the outliers of classes (step 2.2)
############################################################################################

def get_class_barplot(class_name, csv_name, sd=2, col="faces"):

    # get stats on selected class
    objStats = pd.read_csv(csv_name)
    class_objStats = objStats[objStats["class"] == class_name].sort_values([col], ascending=[False])

    # get outliers
    col_list = class_objStats[col].tolist()
    col_arr = np.array(col_list)

    mean = np.mean(col_arr, axis=0)
    std = np.std(col_arr, axis=0)

    final_list = [x for x in col_arr if (x > mean - sd * std)]
    final_list = [x for x in final_list if (x < mean + sd * std)]

    # recolor outliers
    objcolors = ["lightslategray",] * (len(col_list) + 1)
    for col_item in col_list:

        if col_item not in final_list:
            objcolors[col_list.index(col_item)] = "crimson"

    # draw barplot
    fig = go.Figure(data=[go.Bar(
        x=class_objStats["name"],
        y=class_objStats[col],
        marker_color=objcolors,
        text=class_objStats[col],
        textposition="outside",
        name="Outliers"
    ),
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name="Normal",
            marker=dict(size=12, color="lightslategray", symbol='square'),
        )
    ])
    fig.add_shape(
        showlegend=True,
        type="line",
        x0=-0.5,
        x1=len(class_objStats) - 0.5,
        y0=mean,
        y1=mean,
        opacity=0.5,
        name="Average"
    )
    fig.add_annotation(
        x=len(class_objStats) - 4.5,
        y=mean + (mean * 0.1),
        xref="x",
        yref="y",
        text=f"μ = {round(mean)}, σ = {round(std, 2)}",
        showarrow=True,
        font=dict(
            family="Courier New, monospace",
            size=16,
            color="#ffffff"
            ),
        align="center",
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#636363",
        ax=20,
        ay=-30,
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ff7f0e",
        opacity=0.8
    )
    fig.update_layout(title_text=f"Amount of {col} for every object in class {class_name} with sd = {sd} from mean")
    fig.show()



# testing area
objClass = "Sign"
sd = 1
col = "vertices" #"faces"

get_class_barplot(objClass, "steps/step2/objStats.csv", sd, col)
get_class_barplot(objClass, "steps/step2/objStatsResampled3k.csv", sd, col)
get_class_barplot(objClass, "steps/step2/objStatsResampled4k.csv", sd, col)
get_class_barplot(objClass, "steps/step2/objStatsResampled4kv2.csv", sd, col)
# RectangleTable
# Bicycle
# Tree
# House
# Sign
# Car, Hand -> 1k aim almost executed perfectly