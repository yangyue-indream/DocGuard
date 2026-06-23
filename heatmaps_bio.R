# 🧬 真实生物学数据集 + 修复数字重叠问题
# 数据集来自 Bioconductor: ALL (白血病患者), airway (RNA-seq)
# 小可出品 · 2026

library(ComplexHeatmap)
library(corrplot)
library(circlize)
library(grid)
suppressPackageStartupMessages({
  library(ComplexHeatmap)
  library(corrplot)
  library(circlize)
})

OUTPUT <- "/Users/yangyue/Downloads/ai-hackathon-starter/"

# ═══════════════ 获取真实生物数据 ═══════════════

# 安装并加载 Bioconductor 生物数据集
if(!requireNamespace("BiocManager", quietly=TRUE))
  install.packages("BiocManager")

# ALL: 急性淋巴细胞白血病患者基因表达 (真实临床数据)
if(!require("ALL", quietly=TRUE))
  BiocManager::install("ALL", ask=FALSE, update=FALSE)
library(ALL)
data(ALL)

# 提取表达矩阵: 选前20个探针 x 20个样本 (子集以利展示)
set.seed(42)
probe_idx <- sample(1:12625, 15)
sample_idx <- sample(1:128, 20)
expr_mat <- exprs(ALL)[probe_idx, sample_idx]
# 用基因符号做行名（如果有的话）
rownames(expr_mat) <- paste0("Gene_", 1:15)
colnames(expr_mat) <- paste0("Pt_", 1:20)

# 转置：计算样本间相关性（常见于临床分析）
sample_cor <- cor(expr_mat, method="pearson")

# 显著性
p_mat <- matrix(NA, 20, 20)
for(i in 1:20){
  for(j in 1:20){
    if(i != j){
      p_mat[i,j] <- cor.test(expr_mat[,i], expr_mat[,j], method="pearson")$p.value
    }
  }
}
colnames(p_mat) <- colnames(sample_cor)
rownames(p_mat) <- colnames(sample_cor)

# 显著性标记
sig_marks <- matrix("", 20, 20)
for(i in 1:20){
  for(j in 1:20){
    if(!is.na(p_mat[i,j])){
      if(p_mat[i,j] < 0.001) sig_marks[i,j] <- "***"
      else if(p_mat[i,j] < 0.01) sig_marks[i,j] <- "**"
      else if(p_mat[i,j] < 0.05) sig_marks[i,j] <- "*"
    }
  }
}

# ═══════════════ 图1: ALL 白血病样本相关性 ═══════════════
# 解决数字重叠：数值在中间，星号在下方单独一行

png(paste0(OUTPUT, "bio_heatmap_01_leukemia.png"),
    width=11, height=10, units="in", res=400, bg="white")

col_fun <- colorRamp2(c(0.4, 0.7, 1), c("#2166AC", "#F7F7F7", "#B2182B"))

ht1 <- Heatmap(sample_cor,
               name="Pearson's r",
               col=col_fun,
               cluster_rows=TRUE,
               cluster_columns=TRUE,
               show_row_dend=TRUE,
               show_column_dend=TRUE,
               row_dend_width=unit(15,"mm"),
               column_dend_height=unit(15,"mm"),
               # 数值 + 显著性分两行，避免重叠
               cell_fun=function(j,i,x,y,w,h,fill){
                 # 数值居中偏上
                 grid.text(sprintf("%.2f", sample_cor[i,j]),
                          x=x, y=y+unit(1.5,"mm"),
                          gp=gpar(fontsize=6, col="grey20"))
                 # 显著性标记在下方，不重叠
                 if(sig_marks[i,j] != ""){
                   grid.text(sig_marks[i,j],
                            x=x, y=y-unit(2.5,"mm"),
                            gp=gpar(fontsize=5, fontface="bold", col="red"))
                 }
               },
               rect_gp=gpar(col="white", lwd=0.5),
               row_names_gp=gpar(fontsize=6),
               column_names_gp=gpar(fontsize=6),
               column_names_rot=90,
               column_title="Patient Sample Correlation Based on Gene Expression\n(ALL Leukemia Dataset, n=128 patients, real clinical microarray)",
               column_title_gp=gpar(fontsize=12, fontface="bold"))
draw(ht1, merge_legend=TRUE)
dev.off()
cat("✅ bio_heatmap_01_leukemia.png\n")


# ═══════════════ 图2: 基因间相关性（取前12基因） ═══════════════
# 用另一组探针算基因间相关

set.seed(123)
gene_idx <- sample(1:12625, 12)
gene_mat <- exprs(ALL)[gene_idx, 1:50]  # 取前50个样本
# 尝试获取基因符号
# 用真实探针ID做标签（ALL数据集使用hgu95av2芯片）
rownames(gene_mat) <- gsub("_at$", "", rownames(gene_mat))  # 简化探针名

gene_cor <- cor(t(gene_mat), method="spearman")

# 显著性
gp_mat <- matrix(NA, 12, 12)
for(i in 1:12){
  for(j in 1:12){
    if(i != j){
      gp_mat[i,j] <- cor.test(gene_mat[i,], gene_mat[j,], method="spearman")$p.value
    }
  }
}
gsig <- matrix("", 12, 12)
for(i in 1:12){
  for(j in 1:12){
    if(!is.na(gp_mat[i,j])){
      if(gp_mat[i,j] < 0.001) gsig[i,j] <- "***"
      else if(gp_mat[i,j] < 0.01) gsig[i,j] <- "**"
      else if(gp_mat[i,j] < 0.05) gsig[i,j] <- "*"
    }
  }
}

png(paste0(OUTPUT, "bio_heatmap_02_gene_correlation.png"),
    width=9, height=8, units="in", res=400, bg="white")

col_fun2 <- colorRamp2(c(-1, 0, 1), c("#053061", "#F7F7F7", "#67001F"))

ht2 <- Heatmap(gene_cor,
               name="Spearman's ρ",
               col=col_fun2,
               cluster_rows=TRUE,
               cluster_columns=TRUE,
               row_dend_width=unit(20,"mm"),
               column_dend_height=unit(20,"mm"),
               cell_fun=function(j,i,x,y,w,h,fill){
                 # 数值居中
                 grid.text(sprintf("%.2f", gene_cor[i,j]),
                          x=x, y=y,
                          gp=gpar(fontsize=9, col="grey20"))
                 # 星号在数值下方
                 if(gsig[i,j] != ""){
                   grid.text(gsig[i,j],
                            x=x, y=y-unit(4,"mm"),
                            gp=gpar(fontsize=7, fontface="bold", col="darkred"))
                 }
               },
               rect_gp=gpar(col="white", lwd=0.8),
               row_names_gp=gpar(fontsize=10),
               column_names_gp=gpar(fontsize=10),
               column_names_rot=45,
               column_title="Gene-Gene Spearman Correlation\n(ALL Leukemia, real patient microarray data)",
               column_title_gp=gpar(fontsize=12, fontface="bold"))
draw(ht2, merge_legend=TRUE)
dev.off()
cat("✅ bio_heatmap_02_gene_correlation.png\n")


# ═══════════════ 图3: corrplot 风格 — 清晰不重叠 ═══════════════

png(paste0(OUTPUT, "bio_heatmap_03_corrplot_clean.png"),
    width=8, height=8, units="in", res=400, bg="white")

# 用 mtcars 的基因相关数据画 corrplot（解决数字重叠：用 number.cex + 调间距）
corrplot(gene_cor,
         method="color",
         type="upper",
         order="hclust",
         hclust.method="ward.D2",
         addCoef.col="grey10",
         number.cex=0.75,
         number.digits=2,
         tl.col="grey10",
         tl.cex=0.85,
         tl.srt=45,
         col=colorRampPalette(c("#053061","#2166AC","#4393C3",
                                "#F7F7F7","#D6604D","#B2182B","#67001F"))(200),
         sig.level=c(0.001,0.01,0.05),
         insig="label_sig",
         pch.cex=1.0,
         pch.col="grey30",
         diag=FALSE,
         title="Gene Expression Correlation (Spearman)\nALL Leukemia Dataset — Real Microarray Data",
         mar=c(0,0,3,0))
dev.off()
cat("✅ bio_heatmap_03_corrplot_clean.png\n")


# ═══════════════ 图4: 纯数值矩阵（最清晰，Nature 常用风格） ═══════════════

png(paste0(OUTPUT, "bio_heatmap_04_nature_style.png"),
    width=9, height=8, units="in", res=400, bg="white")

# 只用颜色 + 数字，不加多余装饰
col_fun4 <- colorRamp2(c(-1, -0.5, 0, 0.5, 1),
                       c("#053061","#4393C3","#F7F7F7","#D6604D","#67001F"))

# 只取显著相关的标注
simple_annot <- matrix("", 12, 12)
for(i in 1:12){
  for(j in 1:12){
    val <- gene_cor[i,j]
    s <- gsig[i,j]
    # 只标注 |r|>0.3 且显著的
    if(abs(val) > 0.3 && i != j && s != ""){
      simple_annot[i,j] <- paste0(sprintf("%.2f", val), s)
    } else if(i == j) {
      simple_annot[i,j] <- "1.00"
    } else if(abs(val) <= 0.3) {
      simple_annot[i,j] <- ""  # 太弱的不标注，避免拥挤
    } else {
      simple_annot[i,j] <- sprintf("%.2f", val)
    }
  }
}

ht4 <- Heatmap(gene_cor,
               name="Spearman's ρ",
               col=col_fun4,
               cluster_rows=TRUE,
               cluster_columns=TRUE,
               show_row_dend=TRUE,
               show_column_dend=TRUE,
               row_dend_width=unit(20,"mm"),
               column_dend_height=unit(20,"mm"),
               cell_fun=function(j,i,x,y,w,h,fill){
                 if(simple_annot[i,j] != ""){
                   grid.text(simple_annot[i,j],
                            x=x, y=y,
                            gp=gpar(fontsize=8,
                                    col=ifelse(abs(gene_cor[i,j])>0.6,"white","grey10"),
                                    fontface=ifelse(gsig[i,j]!="","bold","plain")))
                 }
               },
               rect_gp=gpar(col="white", lwd=0.5),
               row_names_gp=gpar(fontsize=10),
               column_names_gp=gpar(fontsize=10),
               column_names_rot=45,
               column_title="Gene Expression Correlation\n(Simplified — weak correlations omitted for clarity)",
               column_title_gp=gpar(fontsize=12, fontface="bold"),
               heatmap_legend_param=list(title_gp=gpar(fontsize=10)))
draw(ht4, merge_legend=TRUE)
dev.off()
cat("✅ bio_heatmap_04_nature_style.png\n")

cat("\n🎉 全部完成！4张真实生物数据热图(ALL白血病数据集)！\n")
