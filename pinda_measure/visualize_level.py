# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

plt.rcParams['figure.figsize'] = (12.0, 7.0)


def load_df(path):
    df = pd.read_csv(path)
    return df

def pivot_to_mean_height(df):
    """convert X, Y, Z records to a matrix of mean Z values"""
    return pd.pivot_table(index="Y", columns="X", values="Z", data=df)

def show_heatmap(df, title, levels=10):
    df=df[["X","Y","Z"]]
    g0 = df.groupby(["X","Y"])
    g1= g0.agg([np.median])
    g = g1.reset_index()
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
    f.suptitle(title)

def show_pinda_jitter(df):
    kde = df.cycle.max() > 2
    g = sns.FacetGrid(df, row="Y", col="X", margin_titles=True, sharex=False, row_order=list(reversed(df.Y.unique())))
    g.map(sns.distplot, "Z", hist=True, kde=kde, rug=True, hist_kws=dict(
        rwidth=0.8,))

def show_XY_jitter(df):
    kde = False
    df = df[df.X < 1]
    g = sns.FacetGrid(df, row="Y", col="X", margin_titles=True,
                      sharex=False, sharey=False,
                      row_order=list(reversed(df.Y.unique())))
    g.map(sns.distplot, "X_act", hist=True, kde=kde, rug=True, hist_kws=dict(
        rwidth=0.8,))

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        df=load_df(path)
        show_heatmap(df)
        plt.title(path)
    plt.show()

