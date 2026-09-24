# -*- coding: utf-8 -*-
"""Crop each box/diamond from the render and OCR it individually; report."""
import re, subprocess, os
from PIL import Image

svg=open("q1_flowchart_v3.svg",encoding="utf-8").read()
im=Image.open("q1_flowchart_v3.png")
W,H=im.size
sw=float(re.search(r'width="(\d+)"',svg).group(1))
sx=W/sw

# gather boxes
boxes=[]
for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',svg):
    x,y,w,h=map(float,m.groups())
    if x==0 and y==0: continue
    boxes.append((x,y,w,h))
for m in re.finditer(r'<polygon points="500.0,([\d.]+) 800.0,([\d.]+) 500.0,([\d.]+) 200.0,([\d.]+)"',svg):
    pass

# expected labels in order
expected=[
 "开始",
 "读取A1-A3质量数据 & A4-A15配比Loss数据",
 "数据预处理：去重、指标变换、缺失异常处理、22指标分为6语义组",
 "组内取中位数得到6组组得分 G_sg",
 "熵权法计算各组权重 w_g → 计算文本综合质量 S_s、领域平均分 S_d",
 "同域计算各指标百分位秩，计算冲突强度 c_s",
 "否→直接使用综合评分 S_s",
 "是→计算稳健秩评分 S_s*，标记冲突样本",
 "输出质量评分、冲突标记结果",
 "配比训练预处理",
 "和约束线性岭回归",
 "二阶交互岭回归",
 "独立集测试、配对Bootstrap显著性检验、跨尺度检验",
 "输出模型指标，确定模型适用边界（仅1M尺度有效）",
 "结束",
]
# sort boxes top->bottom, left->right
boxes_sorted=sorted(boxes,key=lambda b:(round(b[1]/10),b[0]))
print("=== per-box OCR ===")
i=0
for (x,y,w,h) in boxes_sorted:
    crop=im.crop((int(x*sx),int(y*sx),int((x+w)*sx),int((y+h)*sx)))
    crop=crop.resize((crop.width*2,crop.height*2),Image.LANCZOS)
    crop.save("/tmp/box.png")
    r=subprocess.run(["tesseract","/tmp/box.png","stdout","-l","chi_sim"],
                     capture_output=True,text=True)
    txt=" ".join(r.stdout.split())
    print(f"[{i}] y={y:.0f} x={x:.0f} :: {txt}")
    i+=1
