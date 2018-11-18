# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['figure.figsize'] = (12.0, 7.0)
df = pd.read_csv("~/Projects/prusa-level/results.201810261927.csv",sep="\t")


df1=df
df=df1[df1["phase"]=="sweep"]
df3=df.reset_index().groupby(["temp","cycle"])["Z"].mean().unstack()
df3m = df3.interpolate('index').rolling(20, center=True, win_type='hamming').mean()
t35 = df3.loc[35].mean()
df3m -= t35
print(t35)
pl1 = df3m.plot.line(colormap="Accent")
df4 = df3m.loc[[35,55,64]]
sample=3
df5 = df4[sample].reset_index()
df5["dt"]=df5.shift(-1)["temp"]-df5["temp"]
df5["d1"]=df5.shift(-1)[sample]-df5[sample]
df5["k"]=df5["d1"]/df5["dt"]
df3m['k55'] = (df3m.index.values - df5['temp'].loc[1] ) * df5['k'].loc[1] + df5[sample].loc[1] # + 0.02
df3m["k55"].loc[:50] = np.NaN
df3m['k35'] = (df3m.index.values - df5['temp'].loc[0] ) * df5['k'].loc[0] + df5[sample].loc[0] # + 0.01
df3m["k35"].loc[60:] = np.NaN
df3m["k35+0.01"] = df3m['k35'] + 0.01 
df3m["k35-0.01"] = df3m['k35'] - 0.01 
df3m["k55+0.01"] = df3m['k55'] + 0.01 
df3m["k55-0.01"] = df3m['k55'] - 0.01 
pl3 = df3m[[sample,"k35","k55","k35+0.01","k35-0.01","k55+0.01","k55-0.01"]].plot.line(colormap="Accent")
plt.grid()


pl4 = df3.loc[[35::5]].
plt.show()


