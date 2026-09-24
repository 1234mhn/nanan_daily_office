# -*- coding: utf-8 -*-
"""Analyze the PNG: check for text overflow, overlapping boxes, arrows crossing boxes.
Also crop regions and save for manual review."""
from PIL import Image
import sys

im = Image.open(sys.argv[1] if len(sys.argv)>1 else "test.png").convert("L")
W,H = im.size
px = im.load()

def dark(v): return v < 120

# find horizontal runs of dark pixels (box top/bottom edges = long runs)
print("size", W, H)
# detect long horizontal lines
lines=[]
for y in range(H):
    run=0; best=0; bx=0; cur=0
    for x in range(W):
        if dark(px[x,y]):
            if run==0: cur=x
            run+=1
            if run>best: best=run; bx=cur
        else:
            run=0
    if best > W*0.25:
        lines.append((y,bx,best))
# group consecutive
groups=[]
for y,bx,b in lines:
    if groups and y-groups[-1][-1][0]<=2:
        groups[-1].append((y,bx,b))
    else:
        groups.append([(y,bx,b)])
print("long horizontal edges:")
for g in groups:
    ys=[t[0] for t in g]; xs=[t[1] for t in g]; bs=[t[2] for t in g]
    print(f"  y={min(ys)}-{max(ys)} x_from={min(xs)} len={max(bs)}")
