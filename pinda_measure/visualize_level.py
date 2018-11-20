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

def show_heatmap(df):
    df=df[["X","Y","Z"]]
    def span(x):
        return max(x) - min(x)
    g = df.groupby(["X","Y"]).agg([np.mean, span, max, min]).reset_index()
    x = list(map(float,g["X"].values))
    y = list(map(float,g["Y"].values))
    z_mean = list(map(float,g[("Z", "mean")].values))
    z_span = list(map(float,g[("Z", "span")].values))
    z_min = list(map(float,g[("Z", "min")].values))
    z_max = list(map(float,g[("Z", "max")].values))
    f, ax = plt.subplots(2,2, sharex=True, sharey=True)
    def tric(ax, label, d=None, txt=None):
        z = list(map(float,g[("Z", label)].values))
        c = ax.tricontourf(x, y, z, 20)
        ax.plot(x, y, "ko ")
        ax.set_title(txt or label)
        f.colorbar(d or c, ax=ax)
        return c
    c00 = tric(ax[0][0], "mean")
    c01 = tric(ax[0][1], "span", txt="span (max-min)")
    c10 = tric(ax[1][0], "min")
    c11 = tric(ax[1][1], "max")
    f.suptitle("G30 mesh bed level probe")

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        df=load_df(path)
        show_heatmap(df)
        plt.title(path)
    plt.show()

