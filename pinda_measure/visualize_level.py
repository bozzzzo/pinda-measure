# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.tri as tri
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
    g = median_z(df)
    ax = _show_heatmap(resample(g).reset_index(), title=title, levels=levels)
    ax.plot(g.X, g.Y, "ko ")

def _show_heatmap(g, title, levels):
    f, ax = plt.subplots(1,1, sharex=True, sharey=True)
    cs = ax.tricontour(g.X, g.Y, g.Z, levels=levels, linewidths=0.5, colors='k')
    ax.clabel(cs)
    c = ax.tricontourf(g.X, g.Y, g.Z, levels=levels * 5, cmap="RdBu_r")
    ax.set_title("median")
    f.colorbar(c, ax=ax)
    f.suptitle(title)
    return ax

def median_z(df):
    df=df[["X","Y","Z"]]
    g0 = df.groupby(["X","Y"])
    g1= g0.agg(np.median)
    g = g1.reset_index()
    return g

def resample(df, n=50):
    t = tri.Triangulation(df.X, df.Y)
    def rng(t):
        return np.linspace(t.min(), t.max(), n)
    xi, yi = np.meshgrid(rng(df.X), rng(df.Y))
    interp = tri.CubicTriInterpolator(t, df.Z)
    zi = interp(xi, yi)
    dfi = pd.DataFrame(dict(Z=zi.flatten()),
                    index=pd.MultiIndex.from_tuples(zip(xi.flatten(),
                                                        yi.flatten()),
                                                    names=["X", "Y"]))
    return dfi

def show_delta_heatmap(df, odf, title, levels=10, n=50):
    g = median_z(df)
    og = median_z(odf)
    ax = _show_heatmap((resample(g, n=n) - resample(og, n=n)).reset_index(),
                       title=title, levels=levels)
    ax.plot(og.X, og.Y, "rx ")
    ax.plot(g.X, g.Y, "g+ ")

def show_pinda_jitter(df):
    span = df.groupby(["X","Y"])["Z"].agg(lambda z: abs(max(z) - min(z))).max()
    span = np.ceil(span * 200 + 3) / 200

    g = sns.FacetGrid(df, row="Y", col="X", margin_titles=True, sharey=False, sharex=False, row_order=list(reversed(df.Y.unique())))
    def safedistplot(a, *args, **kwargs):
        try:
            sns.distplot(a, *args, **kwargs)
        except:
            kwargs["kde"] = False
            sns.distplot(a, *args, **kwargs)
        m = np.ceil(np.mean(a) * 100) / 100
        ax = kwargs.get("ax", plt.gca())
        ax.set_xlim(m - span / 2, m + span / 2)
    g.map(safedistplot, "Z", bins=10, hist=True, kde=False, rug=True, hist_kws=dict(
        
        rwidth=0.95,))

def show_XY_jitter(df):
    kde = False
    df = df[df.X < 1]
    g = sns.FacetGrid(df, row="Y", col="X", margin_titles=True,
                      sharex=False, sharey=False,
                      row_order=list(reversed(df.Y.unique())))
    g.map(sns.distplot, "X_act", bins=10, hist=True, kde=kde, rug=True,
          hist_kws=dict(rwidth=0.8,))

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        df=load_df(path)
        show_heatmap(df)
        plt.title(path)
    plt.show()

