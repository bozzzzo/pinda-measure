# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['figure.figsize'] = (12.0, 7.0)


def load_df(path):
    df = pd.read_csv(path)
    df["X"] = df["X"]
    df["Y"] = df["Y"]
    return df

def pivot_to_mean_height(df):
    """convert X, Y, Z records to a matrix of mean Z values"""
    return pd.pivot_table(index="Y", columns="X", values="Z", data=df)

def show_heatmap(df, levels=10):
    df=df[["X","Y","Z"]]
    g = df.groupby(["X","Y"]).agg([np.median]).reset_index()
    x = list(map(float,g["X"].values))
    y = list(map(float,g["Y"].values))
    z = list(map(float,g[("Z", "median")].values))
    f, ax = plt.subplots(1,1, sharex=True, sharey=True)
    cs = ax.tricontour(x, y, z, levels=levels, linewidths=0.5, colors='k')
    ax.clabel(cs)
    c = ax.tricontourf(x, y, z, levels=levels * 5, cmap="RdBu_r")
    ax.plot(x, y, "ko ")
    ax.set_title("median")
    f.colorbar(c, ax=ax)
    f.suptitle("G30 mesh bed level probe")

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        df=load_df(path)
        show_heatmap(df)
        plt.title(path)
    plt.show()

