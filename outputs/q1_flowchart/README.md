# Q1 解题思路流程图（问题一）

> 论文《算力约束下提升大语言模型能力的资源配置建模》（华为杯研赛 F 题）第一问技术路线图。

## 文件说明

| 文件 | 类型 | 用途 |
|:--|:--|:--|
| `q1_flowchart.svg` | 纯手写 SVG 矢量源文件 | 主源文件，可直接插入 LaTeX（`\includegraphics`）或 Word；不依赖外部字体文件 |
| `q1_flowchart.png` | 位图（3600×4800 px，等效 300dpi+） | 通用插入版本，适合 Word / PPT |
| `q1_flowchart.drawio` | draw.io (mxGraph XML) | 可视化编辑源文件，双击用 draw.io / diagrams.net 打开即可改字 |
| `README.md` | 本文件 | 说明 |

## 图形内容

一条自上而下的 8 环节主链（单向箭头连接）：

1. ① A1–A3 质量记录（272505 条 / 22 项指标）
2. ② 指标方向统一与机制变换（logit差、softmax期望、ln(1+x)）
3. ③ Min-Max 归一化到 [0,1]
4. ④ 六语义组分组 → 组内取中位数
5. ⑤ 组间熵权 → 文本质量分 S_s → 领域质量分 S_d
6. ⑥ 域内百分位秩极差 → 冲突标记（δ=0.9680，约10%）+ 加权中位数稳健秩评分 S_s*
7. ⑦ 领域配比模型：和约束线性模型（基线）+ 二阶岭回归（预测）
8. ⑧ 同尺度 1M 独立检验（R² 0.3215→0.5392）+ 配对 Bootstrap；跨尺度 1B 诊断 R²=-8.6627 → 限定"参考配比邻域"适用边界

**视觉规范**：仅用 2 种颜色（主链白底 + 深灰边框；关键输出/结论框 —— 第⑤⑥⑧环节 —— 用极浅灰底 #F2F2F2 区分）；无渐变、无阴影、无圆角装饰、无彩色图标。

## 如何改文字

### 方式一：draw.io（推荐，最简单）
1. 打开 https://app.diagrams.net 或桌面版 draw.io
2. 菜单 `File > Open`，选择 `q1_flowchart.drawio`
3. 双击任意方框改字；拖拽调整位置
4. 改完 `File > Export as > SVG`（勾选 "Include a copy of my diagram" 取消勾选）或 `PNG`（选 300dpi / Zoom 400%）

### 方式二：直接改 SVG
- 用文本编辑器打开 `q1_flowchart.svg`
- 方框：`<rect>` 控制位置和大小（x/y/width/height）
- 文字：`<text>` 中的内容直接改；`font-size` 控制字号
- 改完重新导出 PNG（见下）

### 重新导出 PNG（保持 300dpi 清晰度）
```bash
cd /root/.openclaw/workspace/outputs/q1_flowchart
cairosvg q1_flowchart.svg -o q1_flowchart.png --output-width 3600
```
其他可选工具：`rsvg-convert -w 3600 q1_flowchart.svg -o q1_flowchart.png`

## 插入论文建议
- **LaTeX**：`\includegraphics[width=\linewidth]{q1_flowchart.pdf}`（建议先用 inkscape 把 SVG 转 PDF 以获得最佳矢量效果）
- **Word**：直接插入 `q1_flowchart.png`
- 图注已在图内底部："图 X 问题一解题思路：质量评价与领域配比建模流程"，插入后可自行调整编号 X
