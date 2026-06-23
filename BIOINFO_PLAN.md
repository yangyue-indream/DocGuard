# 🧬 生信分析接单方案

## 💰 五大可卖服务（按单价排序）

### 1. RNA-seq 差异表达分析 · $300-800/次
**客户**: 研究生、博士后、生物公司
**你做什么**:
- 接收 raw counts + metadata
- DESeq2/edgeR 差异分析
- 火山图、热图、PCA 图
- 输出：显著差异基因列表 + 精美图表

**工具**: R (DESeq2, ggplot2, pheatmap)
**交付**: 3-5天

### 2. GO/KEGG 富集分析 · $150-400/次
**客户**: 有差异基因列表的研究者
**你做什么**:
- 输入差异基因列表
- clusterProfiler 跑 GO (BP/MF/CC) + KEGG
- 输出：dotplot, barplot, cnetplot, 富集表格

**工具**: R (clusterProfiler, enrichplot)
**交付**: 1-2天

### 3. 序列比对 + 系统发育树 · $200-500/次
**客户**: 做进化/分类的研究者
**你做什么**:
- MSA (muscle/clustalo)
- 建树 (IQ-TREE / RAxML / MrBayes)
- 美化树 (ggtree / iTOL)

**工具**: CLI + R (ggtree, ape)
**交付**: 2-4天

### 4. 蛋白质结构预测/分析 · $300-1000/次
**客户**: 结构生物学/药物设计
**你做什么**:
- AlphaFold/ColabFold 预测
- PyMOL 可视化
- 结构比对、结合位点分析

**工具**: ColabFold, PyMOL, Biopython
**交付**: 3-7天

### 5. 定制生信脚本/Pipeline · $200-600/次
**客户**: 需要自动化的实验室
**你做什么**:
- 自动化分析流程 (Snakemake/Nextflow)
- 数据清洗脚本
- 定制可视化

**工具**: Python/R/Bash
**交付**: 2-5天

---

## 🎯 去哪找客户

| 平台 | 怎么找 | 靠谱度 |
|------|------|:--:|
| **ResearchGate** | 搜 "need bioinformatics help" 帖子 | ⭐⭐⭐⭐ |
| **Reddit r/bioinformatics** | 有人发帖求助，直接 DM | ⭐⭐⭐⭐⭐ |
| **Twitter/X** | 搜 "need help RNA-seq analysis" | ⭐⭐⭐ |
| **Upwork** | 搜 "bioinformatics" "RNA-seq" | ⭐⭐⭐ |
| **Fiverr** | 挂生信 Gig（竞争少！） | ⭐⭐⭐⭐ |
| **大学/医院** | 直接联系 PI/博士后 | ⭐⭐⭐⭐⭐ |
| **Biostars.org** | 回答问题→建立声誉→接单 | ⭐⭐⭐ |

---

## 🛠️ 工具箱

| 任务 | R | Python | CLI |
|------|------|------|------|
| 序列处理 | Biostrings | BioPython | seqkit |
| 比对 | Rsubread | pysam | STAR, bowtie2 |
| 差异表达 | **DESeq2**, edgeR | pydeseq2 | - |
| 富集分析 | **clusterProfiler** | gseapy | - |
| 建树 | ape, ggtree | Bio.Phylo | **IQ-TREE** |
| 可视化 | **ggplot2**, pheatmap | matplotlib, seaborn | - |

---

## 🚀 怎么开始

### 第1步: 做一个作品（今天）
选RNA-seq分析，拿公开数据集做一个完整的分析报告
→ GEO 数据库下载 GSE 数据
→ DESeq2 分析
→ 出图 + 写结论
→ 这就是你的 Portfolio

### 第2步: 挂到 Fiverr（明天）
```
Gig Title: "I will analyze your RNA-seq data with DESeq2 and enrichment analysis"
定价: Basic $200 / Standard $400 / Premium $800
```

### 第3步: 去 Reddit/Biostars 接单（持续）
- 每天花15分钟看 r/bioinformatics
- 回答简单问题建立信任
- 有人需要帮忙时提报价

---

## 💡 为什么你能赢

1. **你有生物背景** — 懂实验设计、懂生物学意义
2. **你有我和 Claude Code** — R/Python 代码我帮你写，分析速度翻倍
3. **竞争者少** — 全球能做这个的人远少于普通开发者
4. **客户有钱** — 课题组经费、公司预算，$500 对他们不算什么
5. **复购** — 一个实验室会反复找你
