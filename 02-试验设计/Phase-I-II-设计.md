# Phase I–II 临床试验设计笔记

> 参考资源：[christos-athanasakopoulos/clinical-trial-design-RCT](https://github.com/christos-athanasakopoulos/clinical-trial-design-RCT)

---

## 1. Phase I 设计

Phase I 试验的主要目标是确定**最大耐受剂量（Maximum Tolerated Dose, MTD）**，即在不产生不可接受毒性的前提下可给予患者的最高剂量水平。

### 1.1 3+3 法（经典剂量递增设计）

**设计原理：**

- 从最低剂量开始，每组 **3 名患者**接受同一剂量水平
- 观察剂量限制性毒性（DLT）发生率
- 根据 DLT 结果决定下一步行动：

| 3 例患者中 DLT 数量 | 决策 |
|:---:|:---|
| 0 | 递增到下一剂量水平 |
| 1 | 同剂量再入组 3 例（共 6 例） |
| 2 或 3 | 停止递增，MTD 为前一剂量水平 |

**扩展规则（6 例 Cohort）：**

- 若 6 例中 DLT ≤ 1：递增
- 若 6 例中 DLT ≥ 2：停止，MTD 为前一剂量

**优点：** 简单直观、无需复杂统计模型、被监管广泛接受

**缺点：**
- 保守性强，倾向于**低估 MTD**
- 仅评估有限剂量水平
- 不利用累积数据，效率较低

**操作曲线（Operating Characteristic, OC）计算：**

```r
OC_3plus3 <- function(p, doses = NULL) {
  if (is.null(doses)) {
    doses <- paste("Dose", seq_along(p))
  }
  # Pi = P(在剂量i不递增) = P(0 DLT) + P(1 DLT) × P(下一剂量0 DLT)
  Pi <- dbinom(0, size = 3, prob = p) + 
        dbinom(1, size = 3, prob = p) * dbinom(0, size = 3, prob = p)
  Qi <- cumprod(Pi)  # 累积不递增概率
  OC <- 1 - Qi       # 累积递增概率（操作曲线）
  data.frame(dose = doses, p = p, Pi = Pi, Qi = Qi, OC = OC)
}

# 示例：两个场景
res_ScenA <- OC_3plus3(c(0.08, 0.18, 0.30, 0.45))
res_ScenB <- OC_3plus3(c(0.12, 0.22, 0.28, 0.40))
```

**MTD 选择概率计算：**

```r
# 计算在剂量 i 停止研究的概率
stop_prob <- diff(c(0, res_ScenA$OC))

# MTD 分配概率
MTD_probs <- c(
  None  = stop_prob[1],          # 在剂量1停止 → 无MTD
  Dose1 = stop_prob[2],          # 在剂量2停止 → MTD = Dose1
  Dose2 = stop_prob[3],          # 在剂量3停止 → MTD = Dose2
  Dose3 = stop_prob[4],          # 在剂量4停止 → MTD = Dose3
  Dose4 = 1 - res_ScenA$OC[4]    # 未停止 → MTD = Dose4
)
```

---

### 1.2 CRM（Continual Reassessment Method，连续重估法）

**设计原理：**

- 基于**贝叶斯模型**，持续更新剂量-毒性关系估计
- 假设毒性概率与剂量之间存在单调递增关系（通常用幂函数或指数模型）
- 每完成一个 Cohort 后，利用所有累积数据重新估计 MTD

**核心步骤：**

1. **先验设定**：为每个剂量水平指定目标毒性概率的先验估计
2. **模型拟合**：使用贝叶斯方法拟合剂量-毒性曲线
3. **MTD 估计**：选择最接近目标毒性率（如 25%）的剂量
4. **递增决策**：下一 Cohort 分配到估计的 MTD

**模型示例（幂模型）：**

$$\pi(d) = \psi(d)^\alpha$$

其中 $\pi(d)$ 是剂量 $d$ 的毒性概率，$\psi(d)$ 是先验估计，$\alpha$ 是待估参数。

**优点：**
- 利用所有累积数据，效率更高
- 更准确地定位 MTD
- 可灵活调整目标毒性率

**缺点：**
- 需要统计专业知识
- 计算复杂，需实时建模
- 早期可能分配更多患者到不安全剂量

---

### 1.3 BOIN（Bayesian Optimal Interval Design）

**设计原理：**

- 基于贝叶斯框架的**区间设计**
- 为每个剂量水平设定两个边界：$\lambda_E$（递增边界）和 $\lambda_D$（递减边界）
- 根据观察到的 DLT 率与边界的比较决定递增、保持或递减

**边界计算公式：**

$$\lambda_E = \frac{\log(1-p_T) - \log(1-p_{E})}{\log(p_{E}) - \log(p_T)}$$

$$\lambda_D = \frac{\log(p_D) - \log(p_T)}{\log(p_T) - \log(1-p_{D})}$$

其中 $p_T$ 是目标毒性率（如 0.25），$p_E$ 和 $p_D$ 是递增/递减的容忍阈值。

**决策规则：**

| 观察到的 DLT 率 | 决策 |
|:---:|:---|
| $\hat{p} < \lambda_E$ | 递增到下一剂量 |
| $\lambda_E \leq \hat{p} \leq \lambda_D$ | 保持当前剂量 |
| $\hat{p} > \lambda_D$ | 递减到前一剂量（或停止） |

**优点：**
- 规则简单，易于实施
- 统计性能接近 CRM
- 无需复杂实时建模

**缺点：**
- 边界需预先设定，依赖目标毒性率
- 对极端毒性率场景可能不够灵活

---

### 1.4 三种 Phase I 设计对比

| 特性 | 3+3 法 | CRM | BOIN |
|:---|:---:|:---:|:---:|
| 统计复杂性 | 低 | 高 | 中 |
| 数据利用效率 | 低 | 高 | 中 |
| MTD 准确性 | 保守/偏低 | 高 | 较高 |
| 实施难度 | 简单 | 需建模 | 中等 |
| 监管接受度 | 高 | 增长中 | 增长中 |

---

## 2. Phase II 设计

Phase II 试验主要评估**药物有效性信号**，决定是否进入 Phase III。

### 2.1 单阶段精确二项设计（Exact Binomial Single-Stage）

**假设检验框架：**

$$H_0: p \leq p_0 \quad \text{vs.} \quad H_1: p > p_0$$

- $p_0$：无效假设下的响应率（历史对照）
- $p_1$：备择假设下的目标响应率
- $\alpha$：I 类错误率（通常 0.05 或 0.10）
- $1-\beta$：统计功效（通常 80% 或 90%）

**样本量计算逻辑：**

寻找最小的 $n$ 和临界值 $k$，使得：
- $P(X > k \mid p_0) \leq \alpha$（控制 I 类错误）
- $P(X > k \mid p_1) \geq 1-\beta$（达到目标功效）

**R 代码实现：**

```r
single_stage <- function(p0, p1, alpha, power) {
  n <- 1
  while (TRUE) {
    # 找到最小的 k 使得 P(X > k | p0) <= alpha
    kvec <- 0:n
    ptail0 <- pbinom(kvec, size = n, prob = p0, lower.tail = FALSE)
    idx <- which(ptail0 <= alpha)[1]
    
    if (!is.na(idx)) {
      k_crit <- kvec[idx]  # 若 X > k_crit 则拒绝 H0
      # 计算功效 P(X > k_crit | p1)
      ptail1 <- pbinom(k_crit, size = n, prob = p1, lower.tail = FALSE)
      
      if (ptail1 >= power) {
        return(c(n = n, k = k_crit, alpha_exact = ptail0[idx], power_exact = ptail1))
      }
    }
    n <- n + 1
  }
}

# 示例
res_A <- single_stage(p0 = 0.15, p1 = 0.40, alpha = 0.10, power = 0.80)
res_B <- single_stage(p0 = 0.20, p1 = 0.40, alpha = 0.05, power = 0.90)
```

---

### 2.2 Simon 两阶段设计（Simon Two-Stage Design）

**设计思想：**

- 分两个阶段进行，允许在**无效时提前停止**
- 第一阶段入组 $n_1$ 例患者，若响应数 $\leq r_1$ 则停止试验
- 若响应数 $> r_1$，继续第二阶段，再入组 $n_2$ 例
- 总响应数 $> r$ 时拒绝 $H_0$，认为药物有效

**两种优化目标：**

| 设计类型 | 优化目标 | 适用场景 |
|:---|:---|:---|
| **Optimal（最优）** | 最小化**无效时**的期望样本量 | 多数情况首选 |
| **Minimax（最小最大）** | 最小化**最大样本量** | 资源受限或伦理敏感 |

**R 代码实现（使用 `clinfun` 包）：**

```r
library(clinfun)

# Scenario A: p0=0.15, p1=0.40, alpha=0.10, beta=0.20
simon_A_optimal <- ph2simon(pu = 0.15, pa = 0.40, ep1 = 0.10, ep2 = 0.20, 
                              nmax = 100, opt = "optimal")
simon_A_minimax <- ph2simon(pu = 0.15, pa = 0.40, ep1 = 0.10, ep2 = 0.20, 
                              nmax = 100, opt = "minimax")

# Scenario B: p0=0.20, p1=0.40, alpha=0.05, beta=0.10
simon_B <- ph2simon(pu = 0.20, pa = 0.40, ep1 = 0.05, ep2 = 0.10, nmax = 100)
```

**输出参数解释：**

| 参数 | 含义 |
|:---|:---|
| `n1` | 第一阶段样本量 |
| `r1` | 第一阶段停止边界（≤ r1 则停止） |
| `N` | 总样本量（若进入第二阶段） |
| `r` | 总响应数边界（> r 则拒绝 H0） |
| `En0` | 无效假设下的期望样本量 |
| `En1` | 备择假设下的期望样本量 |

**功效计算（中间响应率场景）：**

当真实响应率介于 $p_0$ 和 $p_1$ 之间时，需手动计算功效：

```r
# 示例：真实 p = 0.30，设计参数 n1=7, r1=1, N=18, r=4
p_true <- 0.30
n1 <- 7; r1 <- 1; N <- 18; r <- 4
n2 <- N - n1

# 仅计算第一阶段响应数 > r1 的情况（试验继续）
x1_vals <- (r1 + 1):n1

power <- sum(
  dbinom(x1_vals, n1, p_true) * 
  pbinom(r - x1_vals, n2, p_true, lower.tail = FALSE)
)
```

**逻辑说明：**
- 第一阶段需观察到 $> r_1$ 个响应才能继续
- 继续后，第二阶段需总响应数 $> r$ 才能拒绝 $H_0$
- 功效 = Σ P(第一阶段 x1) × P(第二阶段 x2 足够)

---

### 2.3 样本量计算逻辑总结

**Phase II 样本量影响因素：**

1. **效应大小**：$p_1 - p_0$ 越大，所需样本量越小
2. **I 类错误 $\alpha$**：越小则样本量越大
3. **功效 $1-\beta$**：越高则样本量越大
4. **设计类型**：两阶段设计在无效时节省样本量

**经验法则（单阶段近似）：**

$$n \approx \frac{(z_{1-\alpha}\sqrt{p_0(1-p_0)} + z_{1-\beta}\sqrt{p_1(1-p_1)})^2}{(p_1 - p_0)^2}$$

---

## 3. 剂量递增规则

### 3.1 3+3 法递增/递减/停止规则

| 当前 Cohort DLT 结果 | 决策 | 下一 Cohort |
|:---|:---|:---|
| 0/3 DLT | 递增 | 下一剂量 +1 |
| 1/3 DLT | 扩展 | 同剂量 +3 例 |
| 0/6 DLT（扩展后） | 递增 | 下一剂量 +1 |
| 1/6 DLT（扩展后） | 递增 | 下一剂量 +1 |
| ≥2/3 DLT | 停止 | 不推荐该剂量，MTD = 前一剂量 |
| ≥2/6 DLT（扩展后） | 停止 | 不推荐该剂量，MTD = 前一剂量 |

### 3.2 BOIN 决策边界表（目标毒性率 25%）

| 剂量水平 | $\lambda_E$（递增边界） | $\lambda_D$（递减边界） |
|:---:|:---:|:---:|
| 3 例 | 0.000 | 0.667 |
| 6 例 | 0.083 | 0.500 |
| 9 例 | 0.111 | 0.444 |
| 12 例 | 0.125 | 0.417 |

**决策表（6 例 Cohort，目标 25%）：**

| DLT 数量 | 决策 |
|:---:|:---|
| 0 | 递增 |
| 1 | 递增 |
| 2 | 保持 |
| 3 | 保持 |
| 4+ | 递减/停止 |

### 3.3 CRM 递增规则

- 计算每个剂量水平的后验毒性概率
- 选择后验中位数最接近目标毒性率（如 25%）的剂量
- 安全约束：不允许跳过剂量递增（除非有充分理由）
- 停止规则：若最高剂量毒性概率 > 目标率 + 容忍度，则停止

---

## 4. 样本量计算逻辑

### 4.1 Phase I 样本量

Phase I 样本量**不是预先固定的**，而是由递增规则动态决定：

- **3+3 法**：最小 3 例（仅 1 个剂量），最大 $3 \times (\text{剂量数} + \text{扩展数})$
- **CRM/BOIN**：通常预设最大样本量（如 20-40 例），由停止规则或最大样本量终止

**经验范围：**
- 肿瘤 Phase I：20-40 例
- 非肿瘤 Phase I：10-30 例

### 4.2 Phase II 样本量

**单阶段设计：**

$$n = \min\{n : \exists k, P(X > k \mid p_0) \leq \alpha, P(X > k \mid p_1) \geq 1-\beta\}$$

**两阶段设计（Simon）：**

- **Optimal**：最小化 $E[n \mid H_0] = n_1 + n_2 \times P(\text{进入第二阶段} \mid H_0)$
- **Minimax**：最小化 $N = n_1 + n_2$

**计算步骤：**

1. 枚举所有可能的 $(n_1, r_1, N, r)$ 组合
2. 对每组组合验证 $\alpha$ 和功效约束
3. 按优化目标选择最优方案

### 4.3 功效计算（两阶段设计）

$$\text{Power} = \sum_{x_1 = r_1+1}^{n_1} P(X_1 = x_1 \mid p) \times P(X_2 > r - x_1 \mid p)$$

其中：
- $X_1 \sim \text{Binomial}(n_1, p)$
- $X_2 \sim \text{Binomial}(n_2, p)$

---

## 5. R 代码实现模板

### 5.1 完整 Phase I–II 设计模板

```r
# ============================================================
# Phase I-II 临床试验设计 R 模板
# ============================================================

# 安装所需包
install.packages(c("clinfun", "blockrand", "gsDesign"))

library(clinfun)
library(blockrand)
library(gsDesign)

# ============================================================
# 1. Phase I: 3+3 法操作曲线
# ============================================================

OC_3plus3 <- function(p, doses = NULL) {
  if (is.null(doses)) {
    doses <- paste("Dose", seq_along(p))
  }
  Pi <- dbinom(0, size = 3, prob = p) + 
        dbinom(1, size = 3, prob = p) * dbinom(0, size = 3, prob = p)
  Qi <- cumprod(Pi)
  OC <- 1 - Qi
  data.frame(dose = doses, p = p, Pi = Pi, Qi = Qi, OC = OC)
}

# 计算 MTD 选择概率
calc_MTD_probs <- function(OC_result) {
  stop_prob <- diff(c(0, OC_result$OC))
  n_doses <- nrow(OC_result)
  probs <- c(
    None = stop_prob[1],
    setNames(stop_prob[2:n_doses], paste0("Dose", 1:(n_doses-1))),
    paste0("Dose", n_doses) = 1 - OC_result$OC[n_doses]
  )
  probs
}

# 示例
p_scenario <- c(0.08, 0.18, 0.30, 0.45)
oc_result <- OC_3plus3(p_scenario)
mtd_probs <- calc_MTD_probs(oc_result)
print(round(mtd_probs, 3))

# ============================================================
# 2. Phase II: 单阶段精确二项设计
# ============================================================

single_stage_design <- function(p0, p1, alpha, power) {
  n <- 1
  while (TRUE) {
    kvec <- 0:n
    ptail0 <- pbinom(kvec, size = n, prob = p0, lower.tail = FALSE)
    idx <- which(ptail0 <= alpha)[1]
    
    if (!is.na(idx)) {
      k_crit <- kvec[idx]
      ptail1 <- pbinom(k_crit, size = n, prob = p1, lower.tail = FALSE)
      
      if (ptail1 >= power) {
        return(data.frame(
          n = n, k = k_crit, 
          alpha_exact = ptail0[idx], 
          power_exact = ptail1
        ))
      }
    }
    n <- n + 1
  }
}

# 示例
design_A <- single_stage_design(p0 = 0.15, p1 = 0.40, alpha = 0.10, power = 0.80)
design_B <- single_stage_design(p0 = 0.20, p1 = 0.40, alpha = 0.05, power = 0.90)
print(round(rbind(design_A, design_B), 3))

# ============================================================
# 3. Phase II: Simon 两阶段设计
# ============================================================

# Optimal 设计
simon_optimal <- ph2simon(pu = 0.15, pa = 0.40, ep1 = 0.10, ep2 = 0.20, 
                           nmax = 100, opt = "optimal")
print(simon_optimal)

# Minimax 设计
simon_minimax <- ph2simon(pu = 0.15, pa = 0.40, ep1 = 0.10, ep2 = 0.20, 
                           nmax = 100, opt = "minimax")
print(simon_minimax)

# 中间响应率的功效计算
calc_two_stage_power <- function(n1, r1, N, r, p_true) {
  n2 <- N - n1
  x1_vals <- (r1 + 1):n1
  power <- sum(
    dbinom(x1_vals, n1, p_true) * 
    pbinom(r - x1_vals, n2, p_true, lower.tail = FALSE)
  )
  return(power)
}

# 示例：使用 Simon optimal 设计参数
power_at_03 <- calc_two_stage_power(
  n1 = simon_optimal$n1, r1 = simon_optimal$r1, 
  N = simon_optimal$n, r = simon_optimal$r, 
  p_true = 0.30
)
cat(sprintf("当真实响应率=0.30时，功效 = %.3f\n", power_at_03))

# ============================================================
# 4. 随机化方案
# ============================================================

# 简单随机化（模拟）
simple_randomization <- function(N, p = 0.5) {
  u <- runif(N)
  arm <- ifelse(u < p, "A", "B")
  table(arm)
}

# 区组随机化
block_randomization <- function(N, block_size = 4) {
  set.seed(123)
  block_rand <- blockrand(
    n = N,
    num.levels = 2,
    levels = c("A", "B"),
    block.sizes = block_size / 2
  )
  table(block_rand$treatment)
  head(block_rand, 20)
}

# ============================================================
# 5. 期中分析（Group Sequential Design）
# ============================================================

# O'Brien-Fleming 边界
of_design <- gsDesign(
  k = 3,
  test.type = 2,
  alpha = 0.025,
  beta = 0.20,
  timing = c(0.3, 0.6, 1.0),
  sfu = "OF"
)
gsBoundSummary(of_design)

# Pocock 边界
pocock_design <- gsDesign(
  k = 3,
  test.type = 2,
  alpha = 0.025,
  beta = 0.20,
  timing = c(0.3, 0.6, 1.0),
  sfu = "Pocock"
)
gsBoundSummary(pocock_design)

# ============================================================
# 6. 结果汇总表
# ============================================================

create_design_summary <- function() {
  data.frame(
    Design = c("3+3", "CRM", "BOIN", "Simon Optimal", "Simon Minimax"),
    Primary_Goal = c("MTD", "MTD", "MTD", "Efficacy Signal", "Efficacy Signal"),
    Sample_Size = c("20-40", "20-40", "20-40", "Variable", "Variable"),
    Early_Stop = c("No", "Yes", "Yes", "Yes", "Yes"),
    Complexity = c("Low", "High", "Medium", "Medium", "Medium")
  )
}

print(create_design_summary())
```

### 5.2 关键 R 包速查

| 包名 | 主要功能 | 关键函数 |
|:---|:---|:---|
| `clinfun` | Phase I/II 设计 | `ph2simon()`, `crm()`, `boin()` |
| `blockrand` | 区组随机化 | `blockrand()` |
| `gsDesign` | 组序贯设计 | `gsDesign()`, `gsBoundSummary()` |
| `TrialDesign` | 综合试验设计 | 多种设计方法 |

---

## 6. 关键要点总结

### Phase I 选择建议

| 场景 | 推荐设计 |
|:---|:---|
| 传统肿瘤药物，监管要求严格 | 3+3 法 |
| 需要高效准确定位 MTD | CRM |
| 平衡简单性和统计性能 | BOIN |
| 细胞/基因治疗（毒性延迟） | 修改版 CRM 或 TITE-CRM |

### Phase II 选择建议

| 场景 | 推荐设计 |
|:---|:---|
| 资源充足，追求精确 | 单阶段精确二项 |
| 希望无效时尽早停止 | Simon 两阶段（Optimal） |
| 最大样本量受限 | Simon 两阶段（Minimax） |
| 多臂或多剂量 | 多臂两阶段设计 |

### 常见陷阱

1. **3+3 法**：不要混淆 DLT 率与 MTD 选择概率
2. **Simon 设计**：功效计算必须考虑两阶段条件概率
3. **样本量**：Phase I 样本量由规则决定，Phase II 需预先计算
4. **期中分析**：需预先设定边界，避免 inflate I 类错误

---

## 7. 进一步阅读

- **Phase I**:
  - O'Quigley et al. (1990). "Continual Reassessment Method". *Biometrics*
  - Liu & Leung (2013). "BOIN Design". *Clinical Trials*
  
- **Phase II**:
  - Simon (1989). "Optimal Two-Stage Designs". *Controlled Clinical Trials*
  - Jung et al. (2004). "Phase II Design Review". *Statistics in Medicine*

- **R 实现**:
  - [clinical-trial-design-RCT GitHub](https://github.com/christos-athanasakopoulos/clinical-trial-design-RCT)
  - `clinfun` R 包文档
  - `gsDesign` R 包文档
