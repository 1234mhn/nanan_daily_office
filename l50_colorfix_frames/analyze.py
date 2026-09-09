#!/usr/bin/env python3
import sys, numpy as np
from PIL import Image

def warm_metrics(path):
    img = Image.open(path).convert('RGB').resize((960,540))
    a = np.asarray(img).astype(np.float32)/255.0
    R,G,B = a[...,0],a[...,1],a[...,2]
    mx = np.maximum(np.maximum(R,G),B)
    mn = np.minimum(np.minimum(R,G),B)
    diff = mx-mn
    # HSV saturation
    sat = np.where(mx>0, diff/np.maximum(mx,1e-5), 0)
    val = mx
    # hue approximation (deg)
    hue = np.zeros_like(mx)
    m = (mx==R)&(G>=B);    hue[m]=60*((G[m]-B[m])/np.maximum(diff[m],1e-5))
    m=(mx==R)&(G<B);       hue[m]=60*((G[m]-B[m])/np.maximum(diff[m],1e-5))+360
    m=(mx==G);             hue[m]=60*((B[m]-R[m])/np.maximum(diff[m],1e-5))+120
    m=(mx==B);             hue[m]=60*((R[m]-G[m])/np.maximum(diff[m],1e-5))+240
    # warm set: red/yellow/orange hue 0-70 (skin) and also 300-360pink/red
    warm = ((hue>=340)|(hue<=70)) & (sat>0.08) & (val>0.06)
    # skin-ish: low-mid sat, R>G>B typical, bright-ish
    skinlike = warm & (R>G) & (G>=B*0.85) & (sat<0.55)
    # hot/oversaturated highlight warm: high value + high sat
    hotwarm = warm & (val>0.75) & (sat>0.35)
    def pct(x): 
        x=x[x>0]
        return (float(x.mean()) if x.size else 0.0, float(np.percentile(x,95)) if x.size else 0.0)
    ms, mp = pct(sat[warm]);  hs,hp=pct(sat[mx>0.03])
    vs = float(val[warm].mean()) if warm.any() else 0
    skin_s = float(sat[skinlike].mean()) if skinlike.any() else 0
    skin_v = float(val[skinlike].mean()) if skinlike.any() else 0
    warm_frac=float(warm.mean()); hotwarm_frac=float(hotwarm.mean()) if mx.size else 0
    over = float((val[warm]>0.92).mean()*100) if warm.any() else 0
    return dict(warmFrac=round(warm_frac,4), warmSatMean=round(ms,3), warmSatP95=round(mp,3),
                skinSatMean=round(skin_s,3), skinValMean=round(skin_v,3),
                wholeSatMean=round(hs,3), warmValMean=round(vs,3),
                hotWarmFracPct=round(hotwarm_frac*100,3),
                warmOver92Pct=round(over,2))

if __name__=="__main__":
    for p in sys.argv[1:]:
        try:
            print(p, warm_metrics(p))
        except Exception as e:
            print(p,"ERR",e)
