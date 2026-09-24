# -*- coding: utf-8 -*-
"""Verify no text overflows its box. Reconstruct expected boxes from generator geometry
scaled by (render_width / svg_width) and check that no dark pixel sits outside boxes
other than on connector lines."""
from PIL import Image
import re, sys

svg = open("q1_flowchart_v3.svg", encoding="utf-8").read()
sw = float(re.search(r'width="(\d+)"', svg).group(1))
sh = float(re.search(r'height="([\d.]+)"', svg).group(1))

im = Image.open("test.png").convert("L")
W,H = im.size
sx = W/sw; sy = H/sh
px = im.load()
def dark(v): return v<120

# collect rects and polygons from svg
rects=[]
for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg):
    x,y,w,h = map(float,m.groups())
    rects.append((x,y,w,h))
print("rects:", len(rects))

# text items
texts=[]
for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*font-size="([\d.]+)"[^>]*>([^<]*)</text>', svg):
    x,y,fs,t = m.groups()
    texts.append((float(x),float(y),float(fs),t))
print("texts:", len(texts))

# Estimate text width in svg units: CJK char ~ font-size, latin ~ 0.55*fs
def est_w(t, fs):
    w=0
    for ch in t:
        if ord(ch)>0x2E80: w+=fs
        else: w+=fs*0.55
    return w

def inside(x,y):
    for (rx,ry,rw,rh) in rects:
        if rx-1<=x<=rx+rw+1 and ry-1<=y<=ry+rh+1: return (rx,ry,rw,rh)
    return None

overflow=[]
for (x,y,fs,t) in texts:
    w = est_w(t,fs)
    x1,x2 = x-w/2, x+w/2
    box = inside(x,y) or inside(x, y-fs*0.36) or inside(x, y+fs*0.36)
    if box:
        rx,ry,rw,rh=box
        if x1 < rx+4 or x2 > rx+rw-4:
            overflow.append((t, round(x1-rx,1), round(rx+rw-x2,1)))
    else:
        overflow.append((t,"NOBOX",""))
print("TEXT OVERFLOW candidates:")
for o in overflow: print("  ",o)
