# 建模分析报告

## 1. 总体建模框架

本赛题是一个四问递进式建模任务，主线为：数据质量评价（Q1）→ 广义标度律（Q2）→ 资源优化配置（Q3）→ 能力演进预测（Q4）。

**核心逻辑链**：
- Q1：从22维质量指标提取综合质量分Q，处理指标冲突，建立17域配比p与Loss的关系
- Q2：将Q和p纳入经典标度律L(N,D)，构建广义标度律L(N,D,Q,p)，分析边际效用与替代关系
- Q3：在算力预算C约束下，优化(N,D,Q,p,L)的资源配置，分析结构性转移
- Q4：从历史Benchmark数据分离规模扩张与技术进步贡献，预测未来能力前沿

**数据集角色**：
- 附件A：质量信号（A1–A3）+ 配比实验（A4–A15）→ Q1
- 附件B：标度律拟合（B1–B5）+ NQ实验（B6–B8）+ 大模型外推（B9–B10）→ Q2
- 附件C：Leaderboard（C1–C3）+ 架构元数据（C7）+ 逐任务评测（C8）+ Loss-Benchmark桥接（C5–C6）→ Q4
- Q3输入来自Q1、Q2结果 + C7架构约束

**关键约束与红线**（来自陷阱清单）：
1. 质量指标方向必须统一为"越高越好"（负向指标做1-归一化）
2. 回归必须报告R²/残差，不能离散化回避评价
3. 验证必须用检验集/外推集，不能用训练集自夸
4. 跨尺度外推必须重新估计或补充尺度项
5. 弹性必须归一化（ε = ∂lnL/∂lnX = (∂L/∂X)·(X/L)）
6. 符号正确性：规模↑/质量↑ → Loss↓（负弹性）；Loss与Benchmark负相关

## 2. 数据处理方案

### 附件A（问题一）

| 文件编号 | 文件名 | 规模 | 字段说明 | 处理要点 |
|---------|--------|------|---------|---------|
| A1 | slimpajama_quality_signal_sample.jsonl.xz | 51,230条×27字段 | 22个质量指标+5辅助字段 | 流式读取；8个列表型字段压缩为标量；覆盖7域 |
| A2 | arxiv_*.jsonl.xz | 17,523条×24字段 | 同A1的22指标 | 扩展集（必用）；arxiv域完整覆盖 |
| A3 | github_*.jsonl.xz | 203,752条×24字段 | 同A1的22指标 | 扩展集（必用）；github域完整覆盖 |
| A4 | train_mixture_1m.csv | 512行×18列 | index + 17域配比 | 训练集；每行和≈1 |
| A5 | train_pile_loss_1m.csv | 512行×14列 | index + 13域Loss | 训练集Loss；4域无Loss列 |
| A6–A7 | test_mixture_1m.csv + loss | 256行 | 同A4/A5 | 检验集1M规模 |
| A8–A9 | test_mixture_60m.csv + loss | 256行 | 同A4/A5 | 检验集60M规模 |
| A10–A11 | test_mixture_1B.csv + loss | 64行 | 同A4/A5 | 检验集1B规模 |
| A12–A13 | est_mixture_10b.csv + loss | 63行 | 配比子集+外推Loss | 外推表10B（标注） |
| A14–A15 | est_mixture_70b.csv + loss | 63行 | 配比子集+外推Loss | 外推表70B（标注） |
| A16 | domain_mapping_guide.csv | 17行×4列 | 17域→质量域映射 | 参考映射表 |

**关键预处理**：
- 质量指标：22个指标中8个列表型需先压缩（如均值/中位数/熵）
- 方向统一：负向指标（如广告含量）做`1 - MinMaxNorm(x)`转换
- 缺失Loss：4域（nih_exporter、enron_emails、europarl、philpapers）无Loss列，说明处理策略
- 单位：配比无量纲（和为1），Loss为交叉熵（自然对数单位）

### 附件B（问题二）

| 文件编号 | 文件名 | 规模 | 性质 | 用途 |
|---------|--------|------|------|------|
| B1 | pythia_training_log_existing.csv | 1,176行×15列 | 真实 | 主拟合数据 |
| B2 | cerebras_training_log.csv | 1,029行×15列 | 半合成 | 族外验证（标注） |
| B3 | training_trajectories/*.csv | 8×500行 | 插值 | 轨迹验证（标注） |
| B4 | scaling_baseline.csv | 57行×5列 | 真实 | 跨族验证 |
| B5 | published_scaling_data.csv | 44行 | 真实 | 文献验证 |
| B6–B8 | supplementary_NQ_experiment*.csv | 360/450/1,704行 | 半合成 | 唯一含Q的数据（标注） |
| B9 | supplementary_large_models.csv | 132行 | 真实 | 大模型元数据 |
| B10 | supplementary_large_baseline.csv | 128行 | 估算 | 大模型外推Loss（标注） |

**关键字段**：
- N_params_B：参数量（单位1e9，即十亿）
- D_tokens_B：训练数据量（单位1e9）
- C_FLOPs_1e21：算力（单位1e21）
- val_loss：验证集交叉熵损失
- Q_score：质量分（仅B6–B8有）

**单位换算**：代入C=6ND时，N和D须乘1e9；C_FLOPs_1e21直接使用

### 附件C（问题四）

| 文件编号 | 文件名 | 规模 | 用途 |
|---------|--------|------|------|
| C1 | leaderboard_cleaned.csv | 4,576行×12列 | 6维Benchmark主表 |
| C2 | leaderboard_enhanced.csv | 4,576行×15列 | C1 + Epoch AI元数据 |
| C3 | leaderboard_extended_timeseries.csv | 4,599行×11列 | 时序扩展（2019–2025） |
| C4 | epoch_all_ai_models.csv | 3,523行×57列 | 全量模型元数据 |
| C5 | loss_benchmark_bridge.csv | 43行 | Loss–Benchmark桥接（原始） |
| C6 | loss_benchmark_bridge_expanded.csv | 75行 | 桥接扩展（高+中可比） |
| C7 | model_architecture_metadata.csv | 45行×7列 | 架构+上下文长度 |
| C8 | detailed_results/ | 1,863目录/1,958 JSON | 逐任务评测（必用） |

**关键字段**：
- Model：模型名称
- #Params (B)：参数量（十亿）
- Submission Date：提交日期（时间轴口径）
- IFEval、BBH、MATH Lvl 5、GPQA、MUSR、MMLU-PRO：6维评测得分
- Hub License：开源许可证
- Type：pretrained/chat标签
- max_position_embeddings：上下文长度L（C7，用于Q3）

**C8处理**：1,863目录，1,958 JSON（4个截断），1,860目录含≥1可解析，1,854模型六维完整。按目录取最新可解析记录。

## 3. 符号说明

### 通用符号
- $N$：模型参数量（单位：十亿参数，Billion）
- $D$：训练数据量（单位：十亿Token，Billion Tokens）
- $C$：总算力预算（单位：FLOPs）
- $L$：验证集交叉熵损失（Loss）
- $Q$：数据质量综合评分（归一化到[0,1]，越高越好）
- $\mathbf{p} = (p_1, \dots, p_{17})$：17域配比向量，$\sum p_i = 1, p_i \geq 0$
- $\mathcal{L}$：上下文窗口长度（Context Length）
- $t$：时间（年份）

### 质量评价（Q1）
- $\mathbf{x}^{(i)} \in \mathbb{R}^{22}$：第$i$个样本的22维质量指标原始向量
- $\tilde{\mathbf{x}}^{(i)}$：方向统一后的质量向量（全部"越高越好"）
- $q_i$：样本级质量分
- $Q_{\text{domain}}$：域级质量分
- $L_{\text{mix}}(\mathbf{p})$：配比$\mathbf{p}$下的Loss

### 标度律（Q2）
- $\alpha, \beta, E$：经典Chinchilla标度律参数
- $\gamma, \delta$：广义标度律中Q和p的参数
- $\epsilon_N, \epsilon_D, \epsilon_Q$：N、D、Q的Loss弹性
- $\sigma_{ND}$：N与D的替代弹性

### 资源优化（Q3）
- $C_{\text{train}}(N,D) = 6ND \times 10^9$：基础训练开销
- $C_{\text{quality}}(Q) = f(Q; Q_0, \theta)$：质量提升开销
- $C_{\text{attn}}(\mathcal{L}, N) = k_1 N \mathcal{L}^2 \times 10^9$：注意力开销
- $\mathcal{L}_{\text{crit}}$：使注意力开销与训练开销相当的临界上下文长度
- $\theta$：成本函数类型参数（指数型/幂函数型/对数渐进型）

### 能力演进（Q4）
- $B(\mathbf{s})$：6维Benchmark综合得分，$\mathbf{s} = (s_1, \dots, s_6)$
- $\Delta B_{\text{scale}}$：规模扩张贡献
- $\Delta B_{\text{tech}}$：技术进步贡献
- $B_{\text{frontier}}(t)$：时刻$t$的能力前沿

## 4. 问题分析

### 问题一：数据质量评价、质量冲突消解与领域配比建模

#### 题目要求
1. 从22维质量指标提取综合质量分Q，覆盖全量数据（A1+A2+A3）
2. 定义并消解质量指标冲突（抽样集分析+扩展集验证）
3. 建立17域配比p与Loss的定量关系，在检验集验证并讨论外推稳健性

#### 输入输出
**输入**：
- 质量信号：A1（51,230条×22指标）+ A2（17,523条）+ A3（203,752条）
- 配方实验：A4–A5（训练512组）、A6–A11（检验3套）、A12–A15（外推2套）
- 域映射：A16

**输出**：
- 样本级质量分$q_i$（272,505条）
- 域级质量分$Q_{\text{domain}}$（arxiv、github及其他域）
- 配比-Loss模型$L_{\text{mix}}(\mathbf{p})$及参数
- 冲突识别与消解规则
- 检验集R²、残差分布、外推误差

#### 建模方案

**子任务1.1：质量指标预处理与方向统一**

1. **列表型字段压缩**：8个多维列表型指标压缩为标量
   - 方法：计算均值、中位数、熵或加权组合
   - 示例：`rps_doc_word_count`若为列表，取均值

2. **方向统一**（避开陷阱：必须统一，不能指望聚类自动吸收）
   - 正向指标（越高越好）：直接保留，如`fineweb_edu`、`fluency_en`
   - 负向指标（越低越好）：做补转换$\tilde{x}_j = 1 - \frac{x_j - \min(x_j)}{\max(x_j) - \min(x_j)}$
   - 识别方法：语义判断（如"广告含量"、"异常符号比例"为负向）+ 与Loss相关性符号验证

3. **归一化**：Min-Max归一化到[0,1]

**子任务1.2：质量冲突定义与识别**

冲突定义（避开陷阱：不能用z分数差>0.5并声称冲突率0%）：
- 定义：对同一文本，若存在指标$x_i$与$x_j$在归一化后满足$|\tilde{x}_i - \tilde{x}_j| > \delta$且二者语义互补（如"教育价值高"vs"广告多"），则存在冲突
- 阈值$\delta$：设为0.6（经验值，敏感性分析）
- 成因分析：
  - 指标维度不同（内容质量 vs 形式质量）
  - 领域特性（arxiv公式多导致可读性低但教育价值高）
  - 噪声样本

**子任务1.3：综合质量评分模型**

方法选择（避开陷阱：不用K-means聚类，不用PCA降维当权重）：
- **方案A（基准）**：加权平均
  $$q_i = \sum_{j=1}^{22} w_j \tilde{x}_{ij}$$
  - 权重来源：与Loss的相关性（绝对值），归一化
  - 优点：可解释，权重有数据依据
  
- **方案B（鲁棒）**：基于回归系数
  - 用A4–A5建立$L \sim \mathbf{x}$的岭回归（处理共线性）
  - 取回归系数绝对值作为权重
  
- **方案C（冲突消解）**：分层评分
  - 先聚类识别冲突模式（如"高学术价值-低流畅度"组）
  - 每组内加权，组间再融合
  
采用方案：A为主（简单可解释），B验证权重稳定性，C用于冲突分析

**子任务1.4：域级质量聚合**

聚合方式：
- arxiv域：A2全量17,523条均值
- github域：A3全量203,752条均值
- 其他5域（从A1抽样）：按域分组均值
- 17域配方体系：通过A16映射表关联

**子任务1.5：配比-Loss建模**

模型形式（避开陷阱：不能OLS直接回归后跨尺度套系数）：

**基础模型**：多元线性回归
$$L(\mathbf{p}) = \beta_0 + \sum_{j=1}^{13} \beta_j p_j + \epsilon$$
- 13个域：有Loss列的域
- 约束：单纯形约束$\sum p_j = 1, p_j \geq 0$

**扩展模型1**：引入质量加权
$$L(\mathbf{p}, \mathbf{Q}) = \beta_0 + \sum_{j=1}^{13} \beta_j p_j / Q_j + \epsilon$$
- $Q_j$：第$j$域的质量分（从1.4获得）
- 假设：质量高的域对Loss的负面贡献小

**扩展模型2**：二次交互项
$$L(\mathbf{p}) = \beta_0 + \sum_j \beta_j p_j + \sum_{j<k} \gamma_{jk} p_j p_k + \epsilon$$
- 捕捉域间协同/冲突效应

**扩展模型3**：尺度调整（跨尺度外推关键）
$$L(\mathbf{p}, N) = \beta_0(N) + \sum_{j} \beta_j(N) p_j + \epsilon$$
- $\beta_0(N) = a_0 + b_0 \log N$（幂律缩放）
- $\beta_j(N) = a_j + b_j \log N$（允许域效应随规模变化）

估计方法：
1. 训练集（A4–A5，512组，1M规模）拟合基础模型
2. 检验集（A6–A11，1M/60M/1B三尺度）验证
3. 外推集（A12–A15，10B/70B）评估稳健性
4. 若基础模型在检验集R²下降>0.1，改用模型3

#### 决策变量
- 质量分权重向量$\mathbf{w} \in \mathbb{R}^{22}$
- 配比系数$\boldsymbol{\beta}$

#### 验证指标
- **拟合优度**：训练集R²、调整R²
- **泛化能力**：检验集R²（三尺度分别报告）
- **外推稳健性**：外推集RMSE、MAPE（相对误差）
- **残差诊断**：正态性检验（Shapiro-Wilk）、异方差检验（Breusch-Pagan）
- **冲突率**：抽样集与扩展集的冲突样本占比

#### 与其他问题的依赖
- 输出$Q_{\text{domain}}$和配比模型$L(\mathbf{p})$供Q2使用

#### 求解方法
1. 质量评分：numpy/pandas矩阵运算，复杂度$O(n \cdot m)$，$n$=样本数，$m$=22
2. 配比建模：岭回归（sklearn.Ridge），复杂度$O(k^3)$，$k$=13（域数）
3. 停止条件：收敛或最大迭代（1000次）

#### 计划生成的图表
1. `figures/q1_quality_distribution.pdf`：质量分分布（箱线图，分域）
2. `figures/q1_conflict_heatmap.pdf`：指标间冲突矩阵热图
3. `figures/q1_domain_quality_bar.pdf`：域级质量分柱状图
4. `figures/q1_loss_vs_mixture.pdf`：实际Loss vs 预测Loss散点图（训练+检验）
5. `figures/q1_residual_plot.pdf`：残差分布图
6. `figures/q1_scale_generalization.pdf`：跨尺度泛化曲线（R²随规模变化）

---

### 问题二：跨维度数据融合与广义标度律

#### 题目要求
1. 构建包含N、D、Q、p的广义标度律$L(N,D,Q,\mathbf{p})$
2. 分析各因素边际效用与弹性
3. 推导质量与规模的替代条件
4. 完成参数估计、检验与验证

#### 输入输出
**输入**：
- Pythia训练日志B1（1,176行，主拟合）
- 族外验证B2（1,029行，半合成标注）
- 轨迹验证B3（8×500行，插值标注）
- 跨族基准B4（57行）+ 文献数据B5（44行）
- NQ实验B6–B8（360/450/1,704行，半合成标注，唯一含Q）
- 大模型数据B9–B10（132+128行，外推标注）
- Q1输出：$Q_{\text{domain}}$和$L(\mathbf{p})$

**输出**：
- 广义标度律参数$(\alpha, \beta, E, \gamma, \delta, \dots)$
- 弹性系数$\epsilon_N, \epsilon_D, \epsilon_Q$
- 替代关系：$\Delta Q$等价于多少$\Delta N$
- 模型R²、残差分布、验证误差

#### 建模方案

**子任务2.1：经典标度律拟合**

经典Chinchilla形式（避开陷阱：不用5次多项式过拟合，不用Box-Cox变换陷阱）：
$$L(N, D) = E + \frac{\alpha}{N^\beta} + \frac{\gamma}{D^\delta}$$
或取对数线性化：
$$\log(L - E) \approx \log\alpha - \beta \log N + \text{(D项类似)}$$

拟合步骤：
1. 用B1（Pythia，1,176点）非线性最小二乘拟合（scipy.optimize.curve_fit）
2. 初值：$E=1.5$（经验），$\alpha, \gamma \sim 1$，$\beta, \delta \sim 0.3$
3. 边界约束：$E>1$，$\alpha,\gamma>0$，$0<\beta,\delta<1$

**子任务2.2：广义标度律设计**

**方案A（乘性质量因子）**：
$$L(N,D,Q) = E + \frac{\alpha}{N^\beta} + \frac{\gamma}{D^\delta} \cdot \phi(Q)$$
- $\phi(Q) = Q^{-\eta}$，$\eta>0$（质量高，Loss低）
- 当$Q=1$（完美质量）时，$\phi(1)=1$，退化为经典形式

**方案B（加性质量修正）**：
$$L(N,D,Q) = E + \frac{\alpha}{N^\beta} + \frac{\gamma}{D^\delta} + \frac{\kappa}{Q^\zeta}$$
- $\kappa>0, \zeta>0$

**方案C（耦合形式）**：
$$L(N,D,Q) = E + \frac{\alpha}{(NQ^\lambda)^\beta} + \frac{\gamma}{(DQ^\mu)^\delta}$$
- 质量与规模耦合

采用方案：A为主（物理直观），B和C作对比验证

**引入配比p**：
- 通过Q1的域级质量$Q_j$和配比$p_j$计算加权质量：
  $$Q_{\text{eff}} = \sum_{j=1}^{17} p_j Q_j$$
- 代入广义标度律

**子任务2.3：弹性分析**（避开陷阱：必须归一化，不能只算有限差分）

定义Loss弹性：
$$\epsilon_X = \frac{\partial \ln L}{\partial \ln X} = \frac{\partial L}{\partial X} \cdot \frac{X}{L}$$

对方案A：
$$\epsilon_N = -\beta \frac{\alpha N^{-\beta}}{L(N,D,Q)} < 0$$
$$\epsilon_D = -\delta \frac{\gamma D^{-\delta} \phi(Q)}{L(N,D,Q)} < 0$$
$$\epsilon_Q = -\eta \frac{\gamma D^{-\delta} Q^{-\eta-1}}{L(N,D,Q)} < 0$$

符号检查（避开陷阱）：规模↑/质量↑应使Loss↓，故弹性应为负

**子任务2.4：替代关系推导**

质量与规模替代条件：$dL = 0$时，
$$\frac{dN}{dQ}\bigg|_{dL=0} = -\frac{\partial L/\partial Q}{\partial L/\partial N}$$

对方案A：
$$\frac{\Delta N}{N} \approx \frac{\eta}{\beta} \frac{\gamma D^{-\delta} Q^{-\eta-1}}{\alpha N^{-\beta}} \frac{\Delta Q}{Q}$$

解释："质量提升0.1"等价于参数量增加的比例

**子任务2.5：参数估计与验证**

数据源：
- 主拟合：B1（Pythia，1,176点）
- Q依赖：B6–B8（NQ半合成实验，360+450+1,704点，标注为半合成）
- 族外验证：B2（Cerebras，1,029点，标注）+ B4（跨族57点）
- 文献验证：B5（44点）
- 大模型外推：B9–B10（132+128点，标注）

拟合策略：
1. 先用B1拟合经典部分$(E,\alpha,\beta,\gamma,\delta)$
2. 用B6联合拟合$\eta$（固定上一步参数）
3. 全数据集联合优化（可选）

验证指标：
- 训练集R²（B1）
- 族外R²（B2、B4）
- 文献R²（B5）
- 大模型外推RMSE（B10，标注为估算）

#### 决策变量
- 标度律参数$(E,\alpha,\beta,\gamma,\delta,\eta,\kappa,\zeta,\lambda,\mu)$（根据方案选择）

#### 验证指标
- R²：分数据集报告（训练/族外/文献/大模型）
- 残差：正态性、异方差
- 弹性符号与量级合理性
- 替代条件数值示例

#### 与其他问题的依赖
- 输入：Q1的$Q_{\text{domain}}$和$L(\mathbf{p})$
- 输出：标度律$L(N,D,Q,\mathbf{p})$供Q3使用

#### 求解方法
- 非线性最小二乘（scipy.optimize.curve_fit或least_squares）
- 初值策略：经典参数从文献，质量参数从小值开始
- 停止条件：残差平方和变化<1e-6或最大迭代5000次
- 复杂度：$O(n \cdot p \cdot iter)$，$n$=样本数，$p$=参数数，iter=迭代次数

#### 计划生成的图表
1. `figures/q2_scaling_law_fit.pdf`：L vs N（固定D）和L vs D（固定N）拟合曲线
2. `figures/q2_quality_impact.pdf`：L vs Q曲线（固定N,D）
3. `figures/q2_residual_distribution.pdf`：残差分布（分数据源）
4. `figures/q2_elasticity_heatmap.pdf`：弹性系数热图（不同N,D,Q点）
5. `figures/q2_substitution_contour.pdf`：等Loss曲线（N-Q平面）
6. `figures/q2_validation_scatter.pdf`：预测Loss vs 实际Loss（分验证集）

---

### 问题三：算力约束下的多维资源联合优化与结构性转移

#### 题目要求
1. 在算力预算$C$约束下优化$(N,D,Q,\mathbf{p},\mathcal{L})$
2. 考察低/中/高三档预算：$10^{21}, 10^{22}, 10^{23}$ FLOPs
3. 分析结构性转移（策略质变）
4. 敏感性分析：成本函数类型、上下文长度$\mathcal{L}$

#### 输入输出
**输入**：
- Q2输出：$L(N,D,Q,\mathbf{p})$
- C7：架构元数据（max_position_embeddings）→ $\mathcal{L}$可行值
- 成本函数参数（附录B）

**输出**：
- 三档预算下的最优配置$(N^*, D^*, Q^*, \mathbf{p}^*, \mathcal{L}^*)$
- 最优Loss $L^*$
- 结构性转移识别与临界点
- 敏感性分析结果

#### 建模方案

**子任务3.1：成本函数构建**

总成本：
$$C_{\text{total}}(N,D,Q,\mathcal{L}) = C_{\text{train}}(N,D) + C_{\text{quality}}(Q) + C_{\text{attn}}(N,\mathcal{L})$$

**基础训练开销**（Chinchilla近似）：
$$C_{\text{train}}(N,D) = 6ND \times 10^9 \text{ FLOPs}$$
- 注意：N、D单位为十亿，需乘$10^9$

**数据质量开销**（三种备选，附录B）：

1. 指数型：
   $$C_{\text{quality}}(Q) = c_1 \exp\left(\frac{Q - Q_0}{s_1}\right), \quad c_1=10^{18}, s_1=0.15$$
   
2. 幂函数型：
   $$C_{\text{quality}}(Q) = c_2 (Q - Q_0)^{p_2}, \quad c_2=5 \times 10^{20}, p_2=3.5$$
   
3. 对数渐进型：
   $$C_{\text{quality}}(Q) = c_3 \left[\log\left(\frac{1}{1-Q}\right)\right]^{p_3}, \quad c_3=10^{19}, p_3=2.0$$

其中$Q_0$为基线质量，从Q1的质量分中位数或均值确定。

**注意力开销**：
$$C_{\text{attn}}(N,\mathcal{L}) = k_1 N \mathcal{L}^2 \times 10^9$$
- $k_1$：经验系数（如0.1，敏感性分析）
- $\mathcal{L}$：上下文长度（从C7获取可行值，如512, 2048, 4096, 8192, 32768）

**临界上下文长度**$\mathcal{L}_{\text{crit}}$：使$C_{\text{attn}} = C_{\text{train}}$

$$k_1 N \mathcal{L}_{\text{crit}}^2 = 6ND \implies \mathcal{L}_{\text{crit}} = \sqrt{\frac{6D}{k_1}}$$

**子任务3.2：优化模型**

**目标函数**：最小化Loss
$$\min_{N,D,Q,\mathbf{p},\mathcal{L}} L(N,D,Q,\mathbf{p})$$

**约束条件**：
1. 算力预算：$C_{\text{total}}(N,D,Q,\mathcal{L}) \leq C_{\text{budget}}$
2. 参数范围：$N_{\min} \leq N \leq N_{\max}$（如0.01B ≤ N ≤ 1000B）
3. 数据范围：$D_{\min} \leq D \leq D_{\max}$（如1B ≤ D ≤ 10000B）
4. 质量范围：$Q_0 \leq Q \leq Q_{\max}$（如0.5 ≤ Q ≤ 0.95）
5. 配比单纯形：$\sum_{j=1}^{17} p_j = 1, p_j \geq 0$
6. 上下文离散选择：$\mathcal{L} \in \{512, 2048, 4096, 8192, 32768, \dots\}$（从C7）

**简化策略**（避免高维优化）：
- **策略1（配比固定）**：用Q1的最优配比$\mathbf{p}^*$固定，只优化$(N,D,Q,\mathcal{L})$
- **策略2（质量-配比解耦）**：先优化$(N,D,\mathcal{L})$，再优化$(Q,\mathbf{p})$
- **策略3（联合优化）**：全变量优化（计算量大，需梯度或启发式算法）

采用策略：策略1为主（降维），策略3验证（若时间允许）

**子任务3.3：结构性转移定义与识别**

定义：当预算$C$跨越某阈值时，最优策略发生质的变化

**转移类型**：
1. **质量优先 → 规模优先**：低预算时$Q^*$接近上界，高预算时$N^*,D^*$快速增长而$Q^*$下降
2. **参数密集 → 数据密集**：N/D比例显著变化
3. **短上下文 → 长上下文**：$\mathcal{L}^*$跳变

**识别方法**：
- 数值指标：计算$\frac{C_{\text{quality}}}{C_{\text{train}}}$比例，阈值如0.1（质量<10%为规模优先）
- 梯度分析：$\frac{dN^*}{dC}, \frac{dQ^*}{dC}$符号变化
- 聚类分析：对不同预算的最优解聚类，识别模式切换点

**子任务3.4：敏感性分析**

变量：
1. 成本函数类型：指数型/幂函数型/对数渐进型
2. 上下文长度$\mathcal{L}$：从C7的分布中选取5个代表值
3. 成本参数：$k_1 \pm 50\%$

输出：
- 最优Loss变化范围（极差/标准差）
- 最优配置变化（敏感变量识别）

#### 决策变量
- $(N, D, Q, \mathbf{p}, \mathcal{L})$或简化为$(N, D, Q, \mathcal{L})$

#### 验证指标
- 约束可行性：检查所有约束是否满足
- 目标函数改进：与基线方案（如均分预算）对比
- Pareto前沿：绘制Loss-Cost权衡曲线
- 稳定性：参数扰动下解的变化

#### 与其他问题的依赖
- 输入：Q2的$L(N,D,Q,\mathbf{p})$、C7的$\mathcal{L}$可行值
- 输出：最优配置供Q4参考（间接）

#### 求解方法
- **方法1（序列二次规划SQP）**：scipy.optimize.minimize，方法='SLSQP'
- **方法2（粒子群优化PSO）**：处理离散$\mathcal{L}$
- **方法3（网格搜索+局部优化）**：$\mathcal{L}$枚举，$(N,D,Q)$局部优化

采用方法：方法1为主（快速），方法2验证（全局性）

复杂度：
- SQP：$O(n_{\text{var}}^3 \cdot n_{\text{iter}})$，$n_{\text{var}} \sim 4$，$n_{\text{iter}} \sim 100$
- PSO：$O(n_{\text{particle}} \cdot n_{\text{iter}} \cdot n_{\text{eval}})$，粒子数50，迭代200

#### 计划生成的图表
1. `figures/q3_optimal_allocation_bar.pdf`：三档预算最优配置柱状图
2. `figures/q3_cost_breakdown_pie.pdf`：成本分解饼图（训练/质量/注意力）
3. `figures/q3_structural_transition.pdf`：结构性转移曲线（N,D,Q vs C）
4. `figures/q3_pareto_front.pdf`：Loss-Cost Pareto前沿
5. `figures/q3_sensitivity_heatmap.pdf`：敏感性热图（成本函数×L）
6. `figures/q3_critical_context_length.pdf`：$\mathcal{L}_{\text{crit}}$ vs N,D曲面

---

### 问题四：技术演进分析与前沿预测

#### 题目要求
1. 分离并量化规模扩张与技术进步的贡献占比
2. 预测未来12或24个月能力前沿
3. 建立Loss-Benchmark映射
4. 不确定性分析

#### 输入输出
**输入**：
- Leaderboard C1/C2（4,576模型，6维Benchmark）
- 时序数据C3（4,599模型，2019–2025）
- 元数据C4（3,523模型，算力/开源信息）
- 桥接数据C6（75模型，Loss+Benchmark）
- 架构数据C7（45模型）
- 逐任务评测C8（1,863目录/1,958 JSON，必用）

**输出**：
- 规模贡献$\Delta B_{\text{scale}}$与技术进步贡献$\Delta B_{\text{tech}}$的占比
- 未来12/24个月能力前沿预测$B_{\text{frontier}}(t_{2027})$、$B_{\text{frontier}}(t_{2028})$
- Loss-Benchmark映射函数$B = f(L)$
- 不确定性区间（95%置信区间）

#### 建模方案

**子任务4.1：数据预处理与筛选**

1. **开源筛选**（避开陷阱：必须说明口径）：
   - 口径：Hub License允许研究复现（如MIT、Apache-2.0、开源协议）
   - 或：Epoch AI的"Open model weights?"字段=True
   - 明确说明：是否要求代码开源、数据集开源
   
2. **模型类型区分**：
   - pretrained：预训练基础模型
   - chat/finetuned：对话/微调模型
   - 分别建模（微调模型能力受基座影响）
   
3. **时间轴口径**：
   - 采用：Submission Date（提交日期）
   - 备选：发布日期、版本日期
   - 说明理由：提交日期最可靠，避免回溯修改
   
4. **C8逐任务聚合**（必用）：
   - 1,863目录，1,958 JSON（4个截断）
   - 处理：按目录取最新可解析JSON，跳过损坏文件
   - 聚合：6维Benchmark = 各任务得分加权平均（权重从C1反推或均权）

**子任务4.2：综合能力度量**

Benchmark综合得分（避开陷阱：不能离散化成等级，不能用分类准确率）：
- **方法1（算术平均）**：$B = \frac{1}{6}\sum_{i=1}^6 s_i$
- **方法2（加权平均）**：$B = \sum_{i=1}^6 w_i s_i$，权重$w_i$由主成分分析确定（但需解释）
- **方法3（综合指数）**：$B = \prod_{i=1}^6 s_i^{w_i}$（几何平均）

采用方法：方法1为主（简单），方法2验证（权重可解释）

**子任务4.3：Loss-Benchmark映射**（避开陷阱：Loss与Benchmark应负相关）

数据源：C6（75模型，高+中可比），按Loss_Comparability分层

**映射模型**：
- **线性**：$B = a - b \cdot L$，$b>0$（Loss↑，Benchmark↓）
- **对数**：$B = a - b \cdot \log L$
- **幂律**：$B = a \cdot L^{-b}$，$b>0$

拟合策略：
1. 高可比样本（Pythia系列）拟合
2. 中可比样本验证
3. 报告R²、残差

误差传播：
- 映射误差对能力预测的影响
- 不确定性区间放大系数

**子任务4.4：规模-时间分解**（避开陷阱：必须分解，不能ARIMA直接外推）

**模型A（加性分解）**：
$$B(N, t) = f_{\text{scale}}(N) + g_{\text{tech}}(t) + \epsilon$$
- $f_{\text{scale}}(N) = a \log N + b$（规模效应，对数增长）
- $g_{\text{tech}}(t) = c \cdot t + d$（技术进步，线性时间趋势）
- 假设：规模与时间独立可加

**模型B（乘性分解）**：
$$B(N, t) = f_{\text{scale}}(N) \cdot g_{\text{tech}}(t)$$
- 技术进步改变规模效率

**模型C（增长会计）**：
$$\Delta B_{\text{total}} = \frac{\partial B}{\partial N} \Delta N + \frac{\partial B}{\partial t} \Delta t$$
- 贡献占比：$\frac{\Delta B_{\text{scale}}}{\Delta B_{\text{total}}}$和$\frac{\Delta B_{\text{tech}}}{\Delta B_{\text{total}}}$

符号检查（避开陷阱）：
- $\frac{\partial B}{\partial N} > 0$（规模↑，能力↑）
- $\frac{\partial B}{\partial t} > 0$（时间推进，技术进步）
- 陷阱：$b_N=-6.2$（规模越大得分越低）是错的

拟合数据：C3（4,599模型，2019–2025）

**子任务4.5：能力前沿预测**

**前沿定义**：
- 每个时间点$t$，在所有已提交模型中，综合得分$B$的最大值（或95分位数）
- 公式：$B_{\text{frontier}}(t) = \max_{i: t_i \leq t} B_i$

**预测模型**：

1. **时间序列外推**（基于历史前沿）：
   - 提取每月/季度的$B_{\text{frontier}}(t)$序列
   - ARIMA/指数平滑外推（但需结合规模-技术分解，避开陷阱）
   
2. **情景分析**（算力增长放缓）：
   - 情景1（悲观）：算力年增长率从50%降至10%
   - 情景2（中性）：降至20%
   - 情景3（乐观）：维持30%
   - 结合Q3的最优配置，计算各情景下的$N(t), D(t)$
   - 代入$L(N,D,Q,\mathbf{p})$，再映射到$B$

3. **不确定性量化**：
   - Bootstrap重采样（历史数据）
   - 蒙特卡洛模拟（参数扰动）
   - 95%置信区间

**子任务4.6：逐任务细粒度分析**（C8必用）

从1,863目录中：
- 选取代表性任务（如MATH、GPQA）
- 分析单任务能力演进
- 识别技术进步的任务特异性（如某些任务主要靠规模，某些靠技术）

#### 决策变量
- 映射参数$(a,b)$
- 分解参数$(\alpha_N, \alpha_t)$
- 外推参数（ARIMA阶数、情景参数）

#### 验证指标
- Loss-Benchmark映射：R²、RMSE、残差正态性
- 规模-时间分解：调整R²、方差分解比例
- 前沿预测：回测误差（用2024年前数据预测2025年，与实际对比）
- 不确定性：区间覆盖率（是否包含实际值）

#### 与其他问题的依赖
- 输入：Q2的$L(N,D,Q,\mathbf{p})$（间接）、Q3的最优配置（情景分析）
- 输出：独立结论

#### 求解方法
- 映射拟合：线性回归/非线性最小二乘
- 分解：多元回归（statsmodels.OLS）
- 时间序列：ARIMA（statsmodels.tsa）
- Bootstrap：重采样1000次
- 复杂度：$O(n \log n)$（排序）+ $O(n \cdot p)$（回归）

#### 计划生成的图表
1. `figures/q4_loss_benchmark_mapping.pdf`：Loss vs Benchmark散点图+拟合曲线（分可比性）
2. `figures/q4_scale_tech_decomposition.pdf`：规模vs技术贡献堆叠柱状图（按年份）
3. `figures/q4_frontier_evolution.pdf`：历史能力前沿曲线（2019–2025）+预测（2026–2028）
4. `figures/q4_scenario_forecast.pdf`：三情景预测对比（悲观/中性/乐观）
5. `figures/q4_uncertainty_bands.pdf`：预测置信区间（95%）
6. `figures/q4_task_specific_trend.pdf`：代表性任务能力演进（C8逐任务）
7. `figures/q4_contribution_pie.pdf`：规模vs技术贡献占比饼图（2019–2025总计）

---

## 5. 假设敏感性预检

### 假设1：质量指标方向识别

**歧义**：某些指标（如`rps_doc_frac_chars_top_2gram`）的优劣方向不明确

**两种解释**：
1. 解释A：高重复字符比例 → 低质量（负向指标）
2. 解释B：适度重复（如学术术语重复）→ 高质量（正向指标）

**验算**：
- 计算该指标与Loss的Pearson相关系数
- 若$r>0$，Loss高时指标高，则为负向指标（需补转换）
- 若$r<0$，Loss低时指标高，则为正向指标（保留）

**最终采用**：基于数据相关性判断，在ANALYSIS_MODELING_REPORT中记录

### 假设2：域级质量聚合方式

**歧义**：抽样集（A1）覆盖7域，扩展集（A2、A3）仅2域，如何得到全17域的质量分？

**两种解释**：
1. 解释A：仅用A1的7域计算，其他10域质量假设为均值
2. 解释B：通过A16映射表建立17域到7域的映射，借用映射域的质量分

**验算**：
- 计算A16映射表的映射类型（direct/near_direct/inferred）分布
- 若>70%为direct，采用解释B（映射可靠）
- 否则采用解释A（保守）

**最终采用**：先检查A16，再决定

### 假设3：配比模型是否需要质量加权

**歧义**：题面未明确要求将Q纳入配比建模

**两种解释**：
1. 解释A：配比模型仅关注$L(\mathbf{p})$，Q留给Q2处理
2. 解释B：配比应考虑域级质量，建模$L(\mathbf{p}, \mathbf{Q})$

**验算**：
- 拟合基础模型$L(\mathbf{p})$，记录R²为$R_1^2$
- 拟合质量加权模型$L(\mathbf{p}, \mathbf{Q})$，记录R²为$R_2^2$
- 若$R_2^2 - R_1^2 > 0.05$，采用解释B（显著改进）

**最终采用**：数据驱动，在Q1实现阶段决定

### 假设4：广义标度律的退化条件

**歧义**：题面提示"Q=1时退化为经典形式"，但Q归一化到[0,1]，实际Q可能不到1

**两种解释**：
1. 解释A：$Q_{\max}$归一化为1（强制），$Q=1$表示最高质量样本
2. 解释B：允许$Q<1$，退化条件改为"$Q=Q_{\max}$时"

**验算**：
- 检查B6–B8的Q_score分布，计算$\max(Q)$
- 若$\max(Q) \approx 1$，采用解释A
- 若$\max(Q) < 0.9$，采用解释B

**最终采用**：基于B6–B8数据

### 假设5：上下文长度的可行集

**歧义**：C7仅45个模型，不能完全代表所有可行的$\mathcal{L}$

**两种解释**：
1. 解释A：仅允许C7中出现的值（保守）
2. 解释B：允许2的幂次（512, 1024, 2048, ..., 131072），C7作验证

**验算**：
- 统计C7的max_position_embeddings分布
- 检查是否集中在2的幂次
- 若>80%为2的幂次，采用解释B

**最终采用**：基于C7分布

## 6. 灵敏度分析与检验方案

### Q1灵敏度分析
1. **质量分权重扰动**：$w_j \pm 20\%$（保持归一化），观察域级质量分变化
2. **冲突阈值$\delta$**：从0.4到0.8，步长0.1，观察冲突率
3. **配比模型正则化参数**：岭回归$\lambda \in [0.01, 10]$，观察系数稳定性

### Q2灵敏度分析
1. **初值影响**：随机扰动初值±50%，观察收敛后参数变化
2. **数据集划分**：Bootstrap重采样（1000次），计算参数95%置信区间
3. **模型形式对比**：方案A/B/C的R²、AIC对比

### Q3灵敏度分析
1. **成本函数类型**：三种成本函数对比，最优Loss差异
2. **上下文长度**：$\mathcal{L} \in \{512, 2048, 8192, 32768\}$，观察最优配置变化
3. **成本参数$k_1$**：$\pm 50\%$，观察$\mathcal{L}_{\text{crit}}$和最优解

### Q4灵敏度分析
1. **映射模型选择**：线性/对数/幂律对比
2. **分解模型选择**：加性/乘性对比
3. **外推时间跨度**：12个月vs 24个月，不确定性变化

### 检验方案

| 问题 | 检验类型 | 方法 | 通过标准 |
|-----|---------|------|---------|
| Q1 | 泛化能力 | 检验集R²（3尺度） | R²>0.7，下降<0.15 |
| Q1 | 外推稳健性 | 外推集MAPE | MAPE<20% |
| Q1 | 残差诊断 | Shapiro-Wilk正态性 | p>0.05 |
| Q2 | 族外验证 | B2、B4验证集R² | R²>0.6 |
| Q2 | 弹性符号 | 符号检查 | $\epsilon_N, \epsilon_D, \epsilon_Q < 0$ |
| Q3 | 约束可行性 | 逐约束检查 | 全部满足，余量>0 |
| Q3 | 基线对比 | Loss改进率 | 优于均分预算>10% |
| Q4 | 回测 | 2024年前预测2025 | RMSE<5分（百分制） |
| Q4 | 映射误差 | R² | R²>0.8 |

## 7. 代码实现任务清单

| 任务 | 输入 | 输出 | 方法 | 校验 |
|-----|------|------|------|------|
| **Q1-1** 质量指标预处理 | A1/A2/A3 JSONL.xz | `results/q1_quality_raw.csv` | 流式读取+列表压缩+方向统一 | 行数=272,505，列数=22 |
| **Q1-2** 质量综合评分 | `q1_quality_raw.csv` | `results/q1_quality_scores.csv` | 加权平均（权重来自相关性） | 分布合理，无NaN |
| **Q1-3** 冲突识别 | `q1_quality_raw.csv` | `results/q1_conflicts.csv` | 阈值法+热图 | 冲突率>0（反陷阱） |
| **Q1-4** 域级质量聚合 | `q1_quality_scores.csv` + A16 | `results/q1_domain_quality.csv` | 分组均值+映射 | 17域完整 |
| **Q1-5** 配比建模（训练） | A4+A5 | `results/q1_mixture_model.pkl` | 岭回归 | R²>0.7 |
| **Q1-6** 配比建模（检验） | A6–A11 + 模型 | `results/q1_validation.csv` | 预测+误差 | 3尺度R²记录 |
| **Q1-7** 配比建模（外推） | A12–A15 + 模型 | `results/q1_extrapolation.csv` | 预测+MAPE | MAPE<20% |
| **Q1-图表** | 上述结果 | `figures/q1_*.pdf`（6张） | matplotlib | 视觉检查 |
| **Q2-1** 经典标度律拟合 | B1 | `results/q2_classic_params.json` | 非线性最小二乘 | 参数合理，$0<\beta,\delta<1$ |
| **Q2-2** 广义标度律拟合 | B1+B6 | `results/q2_general_params.json` | 联合拟合 | $\eta>0$，符号正确 |
| **Q2-3** 弹性计算 | 参数+代表点 | `results/q2_elasticity.csv` | 解析公式 | 全部<0（负弹性） |
| **Q2-4** 替代关系推导 | 参数 | `results/q2_substitution.csv` | 解析公式+数值算例 | 数值合理 |
| **Q2-5** 族外验证 | B2/B4 + 模型 | `results/q2_validation.csv` | 预测+R² | R²>0.6 |
| **Q2-6** 大模型外推 | B9–B10 + 模型 | `results/q2_large_model.csv` | 预测+RMSE | 标注为估算 |
| **Q2-图表** | 上述结果 | `figures/q2_*.pdf`（6张） | matplotlib | 拟合曲线光滑 |
| **Q3-1** 成本函数构建 | 参数 | `code/q3_cost.py` | 三种函数实现 | 单调性检查 |
| **Q3-2** 临界上下文计算 | N,D范围 | `results/q3_critical_L.csv` | 解析公式 | 与C7对照 |
| **Q3-3** 优化求解（低预算） | $C=10^{21}$ | `results/q3_opt_low.json` | SQP+PSO | 约束可行 |
| **Q3-4** 优化求解（中预算） | $C=10^{22}$ | `results/q3_opt_mid.json` | SQP+PSO | 约束可行 |
| **Q3-5** 优化求解（高预算） | $C=10^{23}$ | `results/q3_opt_high.json` | SQP+PSO | 约束可行 |
| **Q3-6** 结构性转移分析 | 三档结果 | `results/q3_transition.csv` | 比例计算+聚类 | 转移点识别 |
| **Q3-7** 敏感性分析 | 参数扰动 | `results/q3_sensitivity.csv` | 重复求解 | 变化范围记录 |
| **Q3-图表** | 上述结果 | `figures/q3_*.pdf`（6张） | matplotlib | Pareto前沿凸性 |
| **Q4-1** 数据筛选 | C1+C4 | `results/q4_filtered.csv` | 开源+类型过滤 | 筛选规则记录 |
| **Q4-2** C8逐任务聚合 | C8目录（1,863） | `results/q4_detailed_agg.csv` | JSON解析+聚合 | 1,854模型完整 |
| **Q4-3** 综合得分计算 | C1或聚合结果 | `results/q4_benchmark.csv` | 加权平均 | 分布合理 |
| **Q4-4** Loss-Benchmark映射 | C6 | `results/q4_mapping_model.pkl` | 回归拟合 | R²>0.8，斜率<0 |
| **Q4-5** 规模-时间分解 | C3 | `results/q4_decomposition.csv` | 多元回归 | 系数符号正确 |
| **Q4-6** 能力前沿提取 | C3时序 | `results/q4_frontier.csv` | 滚动最大值 | 单调非减 |
| **Q4-7** 外推预测 | 前沿+情景参数 | `results/q4_forecast.csv` | ARIMA+情景 | 置信区间覆盖 |
| **Q4-8** 不确定性分析 | 历史数据 | `results/q4_uncertainty.csv` | Bootstrap | 95%区间 |
| **Q4-图表** | 上述结果 | `figures/q4_*.pdf`（7张） | matplotlib | 预测趋势合理 |

**总计**：约40个代码任务，30+张图表

## 8. EVIDENCE_GAP 登记

### 已知缺口

1. **Q1配比模型跨尺度泛化**
   - 缺口：A4–A5仅1M规模训练，检验集跨越1M/60M/1B三尺度，基础线性模型可能失效
   - 影响：Q1配比建模的外推结论可靠性
   - 补齐方式：实现模型3（尺度调整模型），或在结果报告中降低外推结论强度，标注为"基于线性外推假设"

2. **Q1质量指标的4个缺失Loss域**
   - 缺口：nih_exporter、enron_emails、europarl、philpapers无Loss列
   - 影响：配比建模仅用13域，覆盖不完整
   - 补齐方式：说明处理策略（保留配比列但不参与Loss回归，或合并到相似域），在论文中标注

3. **Q2 NQ实验数据为半合成**
   - 缺口：B6–B8为校准+噪声生成，非直接观测
   - 影响：质量Q参数$\eta$的估计可信度
   - 补齐方式：在论文中明确标注"基于半合成数据"，敏感性分析噪声影响，或仅用B6（基础集360点）

4. **Q3上下文长度可行集代表性**
   - 缺口：C7仅45个模型，可能不覆盖全部可行$\mathcal{L}$
   - 影响：$\mathcal{L}$优化的搜索空间
   - 补齐方式：扩展到2的幂次完整集，或在论文中声明"基于C7观测范围"

5. **Q4 Loss-Benchmark映射的可比性分层**
   - 缺口：C6的75个模型中，高可比与中可比混合，Loss来源不统一
   - 影响：映射误差可能被低估
   - 补齐方式：分层拟合并报告分层R²，或仅用高可比样本（约30个）

6. **Q4未来算力增长率假设**
   - 缺口：题面提示"算力增长放缓"，但无具体数值
   - 影响：情景分析的参数设定主观性
   - 补齐方式：查阅文献（如Epoch AI报告），或设定多个情景覆盖范围，标注为"情景假设"

### 当前无缺口声明
若在后续实现中发现新缺口，将更新本节。

---

**报告状态**：待门禁A质询确认后进入实现阶段。
