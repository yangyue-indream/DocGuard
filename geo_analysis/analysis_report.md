# 🧬 RNA-seq 差异表达分析报告
## GSE150910: 间质性肺病的转录组特征比较

---

**分析日期:** 2026-06-23  
**数据集:** GSE150910 (GEO)  
**样本:** 288例人肺组织 (Control: 103 | CHP: 82 | IPF: 103)  
**分析方法:** DESeq2 + clusterProfiler (GO/KEGG)  
**分析工具:** R 4.5.2 + Bioconductor

---

## 📋 1. 研究背景

慢性过敏性肺炎 (CHP) 和特发性肺纤维化 (IPF) 是两种常见的间质性肺病 (ILD)，
临床表现相似但病理机制不同。本研究利用公开 RNA-seq 数据，
系统比较两种疾病与正常肺组织的转录组差异，以揭示其分子特征。

**疾病:**
- **Control:** 正常对照组 (n=103)
- **CHP (Chronic Hypersensitivity Pneumonitis):** 慢性过敏性肺炎 (n=82)
- **IPF (Idiopathic Pulmonary Fibrosis):** 特发性肺纤维化 (n=103)

## 📊 2. 分析流程

```
Raw Counts (18,838 genes × 288 samples)
    ↓ 过滤低表达基因 (≥10 counts in ≥82 samples)
15,700 genes retained
    ↓ DESeq2 负二项模型 + ashr LFC shrinkage
差异表达基因 (|log2FC| > 1, padj < 0.05)
    ↓ clusterProfiler + org.Hs.eg.db
GO Biological Process 富集分析
```

## 🔬 3. 主要发现

### 3.1 整体转录组特征 (PCA)

PCA 分析显示三组样本在转录组层面有明显分离趋势。
PC1 (主成分1) 解释了最大比例的方差，主要区分疾病组与对照组；
PC2 则反映了 CHP 与 IPF 之间的差异。

### 3.2 差异表达基因 (DEGs)

| 对比 | 上调基因 | 下调基因 | 总计 |
|------|:--------:|:--------:|:----:|
| **CHP vs Control** | 898 | 567 | **1,465** |
| **IPF vs Control** | 977 | 420 | **1,397** |
| **IPF vs CHP** | 73 | 160 | **233** |

**重点发现:**
- CHP 和 IPF 共享 **800** 个差异基因，提示两种疾病存在共同的分子通路
- CHP 有更多的下调基因 (567 vs 420)，提示更广泛的转录抑制
- IPF vs CHP 仅 233 个差异基因，说明两种疾病在转录组层面有大量重叠

### 3.3 Top DEGs

**CHP vs Control 最显著差异基因:**

| 基因 | log2FC | 调控方向 | 功能注释 |
|------|:------:|:--------:|----------|
| **IGFL2** | 4.13 | ↑ | 胰岛素样生长因子家族，细胞增殖 |
| **BGN** | 4.29 | ↑ | 双糖链蛋白聚糖，ECM 重构 |
| **COL17A1** | 4.53 | ↑ | XVII型胶原蛋白，基底膜组分 |
| **PTGFRN** | 2.53 | ↑ | 前列腺素F2受体抑制蛋白 |
| **S100A2** | 4.34 | ↑ | S100钙结合蛋白，细胞周期调控 |

**IPF vs Control 最显著差异基因:**

| 基因 | log2FC | 调控方向 | 功能注释 |
|------|:------:|:--------:|----------|
| **IGFL2** | 4.22 | ↑ | 两种疾病均显著上调 |
| **FHL2** | 2.05 | ↑ | 心肌LIM蛋白，TGF-β信号 |
| **CTHRC1** | 2.44 | ↑ | 胶原三螺旋重复蛋白，纤维化标志物 |
| **CDH3** | 2.48 | ↑ | P-钙粘蛋白，上皮-间质转化 |
| **MAP3K15** | -2.44 | ↓ | MAPK信号通路激酶 |

### 3.4 GO 富集分析

#### CHP vs Control — 免疫/炎症特征突出

| GO BP Term | 富集基因数 | 校正P值 |
|------------|:----------:|:--------:|
| Humoral immune response | 56 | 4.34×10⁻¹¹ |
| Antimicrobial humoral response | 36 | 6.17×10⁻⁹ |
| Cell chemotaxis | 61 | 1.29×10⁻⁷ |
| Extracellular matrix organization | 59 | 1.29×10⁻⁷ |
| Leukocyte migration | 69 | 1.29×10⁻⁷ |

**解读:** CHP 表现为典型的**免疫-炎症反应**特征：体液免疫显著激活，
白细胞趋化和迁移增强，同时伴随细胞外基质重塑。这与 CHP 作为免疫介导的过敏性疾病的临床认知一致。

#### IPF vs Control — 纤毛/微管异常突出

| GO BP Term | 富集基因数 | 校正P值 |
|------------|:----------:|:--------:|
| Cilium movement | 72 | 2.43×10⁻²⁷ |
| Cilium-dependent cell motility | 55 | 3.22×10⁻¹⁹ |
| Axoneme assembly | 39 | 3.22×10⁻¹⁹ |
| Microtubule bundle formation | 42 | 2.20×10⁻¹⁶ |
| Humoral immune response | 50 | 1.81×10⁻¹⁰ |

**解读:** IPF 最惊人的特征是**纤毛功能和微管组装**相关通路的极端显著富集
(padj 低至 10⁻²⁷量级)。这提示气道上皮纤毛功能障碍在 IPF 发病中可能扮演关键角色，
是一个值得深入研究的潜在治疗靶点。同时，免疫应答也参与其中。

## 💡 4. 生物学结论

1. **CHP 和 IPF 共享大量转录组变化**（800个共享DEGs），
   反映间质性肺病的共同病理基础（炎症、ECM重塑）。

2. **CHP 的分子特征以免疫-炎症驱动为主**：体液免疫、白细胞趋化、
   抗菌肽反应等通路显著富集，支持其作为免疫介导疾病的分类。

3. **IPF 展现出独特的纤毛功能障碍特征**：纤毛运动相关基因的富集
   显著性远超其他通路（padj ~10⁻²⁷），这为 IPF 的发病机制研究
   提供了新视角——纤毛-微管轴可能是区分 IPF 与 CHP 的关键分子标志。

4. **ECM 重塑是两种疾病的共同特征**：胶原蛋白（COL17A1）、
   蛋白聚糖（BGN）和纤维化标志物（CTHRC1）在两种疾病中均显著上调。

## 🛠️ 5. 方法与可复现性

**完整分析代码:** `deseq2_analysis.R`  
**输入数据:** `data/GSE150910/GSE150910_gene-level_count_file.csv.gz`  
**输出:**
- `results/DEG_*.csv` — 完整差异表达表（含 log2FC, padj, 分类标注）
- `results/GO_BP_*.csv` — GO富集分析结果
- `figures/` — 9张发表级图表（PCA、热图、火山图、GO dotplot）

所有分析可一键复现：
```bash
Rscript deseq2_analysis.R
```

## 📦 6. 交付物清单

| 类型 | 文件 | 用途 |
|------|------|------|
| 🧬 差异表达 | `DEG_*.csv` (3个) | 完整基因列表，可自行筛选下游分析 |
| 🔬 GO 富集 | `GO_BP_*.csv` (3个) | 生物学功能解读 |
| 📈 PCA 图 | `01_pca.png` | 样本整体分布 |
| 🔥 热图 | `02_sample_distance_heatmap.png` | 样本间距离 |
| 🔥 热图 | `03_deg_heatmap.png` | Top DEGs 表达模式 |
| 🌋 火山图 | `volcano_*.png` (3个) | 差异基因可视化 |
| 📊 GO 图 | `GO_BP_*.png` (3个) | 富集通路 dotplot |
| 📝 分析脚本 | `deseq2_analysis.R` | 完整可复现代码 |

---

*本报告由 AI 辅助生成，所有数据分析基于公开数据集 GSE150910 和 Bioconductor DESeq2/clusterProfiler 标准流程。*
