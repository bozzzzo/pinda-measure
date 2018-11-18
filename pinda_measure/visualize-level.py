# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['figure.figsize'] = (12.0, 7.0)


def load_df(path):
    df = pd.read_csv(path, sep="\t")
    df["X"] = df["X"].round()
    df["Y"] = -df["Y"].round()
    return df

def pivot_to_mean_height(df):
    """convert X, Y, Z records to a matrix of mean Z values"""
    return pd.pivot_table(index="Y", columns="X", values="Z", data=df)

def show_heatmap(df):
    plt.contour(df, levels=np.arange(-0.5, 0.5, 0.01), cmap="seismic")
    plt.colorbar()


def show(path):
    plt.figure()
    show_heatmap(pivot_to_mean_height(load_df(path)))
    plt.title(path)

import sys
for path in sys.argv[1:]:
    show(path)
plt.show()

