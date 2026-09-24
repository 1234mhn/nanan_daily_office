# -*- coding: utf-8 -*-
"""Emit a drawio (mxGraph) XML matching q1_flowchart_v3.svg layout."""
import re

svg = open("q1_flowchart_v3.svg", encoding="utf-8").read()

rects=[]
for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg):
    x,y,w,h=map(float,m.groups())
    if x==0 and y==0:   # skip full-canvas background
        continue
    rects.append((x,y,w,h))
polys=[]
for m in re.finditer(r'<polygon points="([^"]+)"', svg):
    pts=[tuple(map(float,p.split(','))) for p in m.group(1).split()]
    polys.append(pts)

# texts in order
texts=[]
for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*font-size="([\d.]+)"[^>]*>([^<]*)</text>', svg):
    x,y,fs,t=m.groups()
    t=t.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&")
    texts.append((float(x),float(y),float(fs),t))

def inside(x,y):
    for (rx,ry,rw,rh) in rects:
        if rx<=x<=rx+rw and ry<=y<=ry+rh: return (rx,ry,rw,rh)
    return None

# group texts into boxes by center
box_texts={}
for (x,y,fs,t) in texts:
    b=inside(x,y) or inside(x,y-fs*0.36)
    if b: box_texts.setdefault(b,[]).append((y,t))

cells=[]
cid=1
idmap={}
for (rx,ry,rw,rh) in rects:
    if rw < 5 or rh < 5:
        continue
    lbl="\n".join(t for _,t in sorted(box_texts.get((rx,ry,rw,rh),[])))
    cells.append((cid,rx,ry,rw,rh,lbl,"rect"))
    idmap[(rx,ry,rw,rh)]=cid
    cid+=1

# diamonds (skip arrowheads which are filled triangles with 3 small pts)
for pts in polys:
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    if len(pts)==4:
        cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
        w=max(xs)-min(xs); h=max(ys)-min(ys)
        # find texts inside
        lbl=[]
        for (x,y,fs,t) in texts:
            if min(xs)<=x<=max(xs) and min(ys)<=y<=max(ys):
                lbl.append((y,t))
        lbl="\n".join(t for _,t in sorted(lbl))
        cells.append((cid,min(xs),min(ys),w,h,lbl,"rhombus"))
        cid+=1

# order cells top-to-bottom then left-to-right (approximate generation order already matches)
xml=[]
xml.append('<mxGraphModel dx="1600" dy="1000" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1000" pageHeight="2000" math="0" shadow="0">')
xml.append('  <root>')
xml.append('    <mxCell id="0"/>')
xml.append('    <mxCell id="1" parent="0"/>')
for (i,x,y,w,h,lbl,shape) in cells:
    st = "rhombus" if shape=="rhombus" else "rectangle"
    lab = lbl.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","&#10;")
    style = (f"rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#3D3D3D;"
             f"strokeWidth=1.6;fontFamily=Noto Sans CJK SC;fontSize=14;fontColor=#000000;"
             f"shape={st};")
    xml.append(f'    <mxCell id="n{i}" value="{lab}" style="{style}" vertex="1" parent="1">')
    xml.append(f'      <mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/>')
    xml.append('    </mxCell>')
xml.append('  </root>')
xml.append('</mxGraphModel>')

open("q1_flowchart_v3.drawio","w",encoding="utf-8").write("\n".join(xml))
print("cells:", len(cells))
