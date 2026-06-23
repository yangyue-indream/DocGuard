#!/usr/bin/env Rscript
# ═══════════════════════════════════════════════════════════════
# 🧬 RNA-seq 差异表达分析 · GSE150910
# 肺部疾病: Control vs CHP vs IPF
# Pipeline: DESeq2 + ggplot2 + clusterProfiler
# ═══════════════════════════════════════════════════════════════

library(DESeq2)
library(ggplot2)
library(pheatmap)
library(RColorBrewer)
library(clusterProfiler)
library(org.Hs.eg.db)
library(enrichplot)
library(dplyr)
library(tidyr)
library(tibble)

# ═══════════════ 1. Load Data ═══════════════
cat("\n📥 Loading data...\n")
counts <- read.csv("data/GSE150910/GSE150910_gene-level_count_file.csv.gz",
                   row.names = 1, check.names = FALSE)

# Create colData from column names
col_names <- colnames(counts)
diagnosis <- factor(sub("_.*", "", col_names), levels = c("control", "chp", "ipf"))
patient_id <- sub(".*_", "", col_names)

colData <- data.frame(
  sample_id = col_names,
  diagnosis = diagnosis,
  patient_id = patient_id,
  row.names = col_names
)

cat(sprintf("  Genes: %d | Samples: %d\n", nrow(counts), ncol(counts)))
cat(sprintf("  Control: %d | CHP: %d | IPF: %d\n",
            sum(diagnosis == "control"), sum(diagnosis == "chp"), sum(diagnosis == "ipf")))

# ═══════════════ 2. DESeq2 Setup ═══════════════
cat("\n🔧 Building DESeq2 object...\n")
dds <- DESeqDataSetFromMatrix(
  countData = counts,
  colData = colData,
  design = ~ diagnosis
)

# Pre-filtering: keep genes with >= 10 counts in at least the smallest group size
smallest_group <- min(table(diagnosis))
keep <- rowSums(counts(dds) >= 10) >= smallest_group
dds <- dds[keep, ]
cat(sprintf("  Genes after filtering: %d (removed %d low-count genes)\n",
            nrow(dds), nrow(counts) - nrow(dds)))

# ═══════════════ 3. Variance Stabilizing Transform ═══════════════
cat("\n📊 Running VST for visualization...\n")
vsd <- vst(dds, blind = TRUE)

# ── 3a. PCA Plot ──
cat("  Generating PCA plot...\n")
pca_data <- plotPCA(vsd, intgroup = "diagnosis", returnData = TRUE)
percentVar <- round(100 * attr(pca_data, "percentVar"))

pca_plot <- ggplot(pca_data, aes(PC1, PC2, color = diagnosis)) +
  geom_point(size = 3, alpha = 0.7) +
  stat_ellipse(level = 0.95, linewidth = 1) +
  scale_color_manual(
    values = c("control" = "#4CAF50", "chp" = "#FF9800", "ipf" = "#E91E63"),
    labels = c("Control", "CHP", "IPF")
  ) +
  labs(
    title = "PCA of RNA-seq Samples",
    subtitle = "GSE150910: Control vs CHP vs IPF",
    x = paste0("PC1: ", percentVar[1], "% variance"),
    y = paste0("PC2: ", percentVar[2], "% variance"),
    color = "Diagnosis"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 18),
    plot.subtitle = element_text(color = "grey40"),
    legend.position = "top"
  )

ggsave("figures/01_pca.png", pca_plot, width = 8, height = 7, dpi = 150)
cat("  ✅ Saved: figures/01_pca.png\n")

# ── 3b. Sample Distance Heatmap ──
cat("  Generating sample distance heatmap...\n")
sample_dists <- dist(t(assay(vsd)))
sample_dist_matrix <- as.matrix(sample_dists)
rownames(sample_dist_matrix) <- paste0(colData$diagnosis, "_", colData$patient_id)
colnames(sample_dist_matrix) <- rownames(sample_dist_matrix)

annotation_col <- data.frame(
  Diagnosis = colData$diagnosis,
  row.names = rownames(colData)
)
ann_colors <- list(Diagnosis = c(control = "#4CAF50", chp = "#FF9800", ipf = "#E91E63"))

png("figures/02_sample_distance_heatmap.png", width = 10, height = 8,
    units = "in", res = 150)
pheatmap(sample_dist_matrix,
         clustering_distance_rows = sample_dists,
         clustering_distance_cols = sample_dists,
         annotation_col = annotation_col,
         annotation_colors = ann_colors,
         show_rownames = FALSE,
         show_colnames = FALSE,
         main = "Sample-to-Sample Distance Heatmap\nGSE150910",
         color = colorRampPalette(rev(brewer.pal(9, "RdBu")))(255))
dev.off()
cat("  ✅ Saved: figures/02_sample_distance_heatmap.png\n")

# ═══════════════ 4. DESeq2 Analysis ═══════════════
cat("\n🧬 Running DESeq2...\n")
dds <- DESeq(dds)

# Function to extract and save DEG results
run_comparison <- function(dds, contrast_name, numerator, denominator,
                           lfc_threshold = 1, padj_threshold = 0.05) {
  cat(sprintf("\n  📋 %s vs %s...\n", numerator, denominator))

  res <- results(dds, contrast = c("diagnosis", numerator, denominator), alpha = padj_threshold)
  res <- lfcShrink(dds, contrast = c("diagnosis", numerator, denominator),
                   res = res, type = "ashr")

  # Add gene symbols + categorize
  res_df <- as.data.frame(res) %>%
    rownames_to_column("gene") %>%
    arrange(padj) %>%
    mutate(category = case_when(
      is.na(padj) | is.na(log2FoldChange) ~ "Not Significant",
      padj < padj_threshold & log2FoldChange > lfc_threshold ~ "Up",
      padj < padj_threshold & log2FoldChange < -lfc_threshold ~ "Down",
      TRUE ~ "Not Significant"
    )) %>%
    mutate(category = factor(category, levels = c("Up", "Down", "Not Significant")))

  # Significant genes
  sig_up <- res_df %>% filter(category == "Up")
  sig_down <- res_df %>% filter(category == "Down")

  cat(sprintf("    Up-regulated: %d | Down-regulated: %d | Total sig: %d\n",
              nrow(sig_up), nrow(sig_down), nrow(sig_up) + nrow(sig_down)))

  # Save full results
  write.csv(res_df, sprintf("results/DEG_%s_vs_%s.csv", numerator, denominator),
            row.names = FALSE)

  # ── Volcano Plot ──
  top_up <- sig_up %>% arrange(desc(log2FoldChange)) %>% head(10)
  top_down <- sig_down %>% arrange(log2FoldChange) %>% head(10)
  top_genes <- bind_rows(top_up, top_down)

  volcano <- ggplot(res_df, aes(x = log2FoldChange, y = -log10(padj), color = category)) +
    geom_point(size = 0.8, alpha = 0.5) +
    scale_color_manual(
      values = c("Up" = "#E91E63", "Down" = "#2196F3", "Not Significant" = "grey80"),
      name = sprintf("|log2FC| > %d & padj < %.2f", lfc_threshold, padj_threshold)
    ) +
    geom_hline(yintercept = -log10(padj_threshold), linetype = "dashed", color = "grey40") +
    geom_vline(xintercept = c(-lfc_threshold, lfc_threshold), linetype = "dashed", color = "grey40") +
    ggrepel::geom_text_repel(
      data = top_genes,
      aes(label = gene),
      size = 3,
      max.overlaps = 15,
      box.padding = 0.5
    ) +
    labs(
      title = sprintf("%s vs %s", numerator, denominator),
      subtitle = sprintf("Up: %d | Down: %d | Total: %d",
                         nrow(sig_up), nrow(sig_down), nrow(sig_up) + nrow(sig_down)),
      x = "log2 Fold Change",
      y = "-log10 Adjusted P-value"
    ) +
    theme_minimal(base_size = 13) +
    theme(
      plot.title = element_text(face = "bold", size = 16),
      legend.position = "top"
    )

  fname <- sprintf("figures/volcano_%s_vs_%s.png", numerator, denominator)
  ggsave(fname, volcano, width = 9, height = 8, dpi = 150)
  cat(sprintf("    ✅ Saved: %s\n", fname))

  return(list(
    contrast = paste(numerator, "vs", denominator),
    res = res_df,
    sig_up = sig_up,
    sig_down = sig_down,
    n_up = nrow(sig_up),
    n_down = nrow(sig_down)
  ))
}

# Run comparisons
comp1 <- run_comparison(dds, "CHP_vs_Control", "chp", "control")
comp2 <- run_comparison(dds, "IPF_vs_Control", "ipf", "control")
comp3 <- run_comparison(dds, "IPF_vs_CHP", "ipf", "chp")

# ═══════════════ 5. Heatmap of Top DEGs ═══════════════
cat("\n🔥 Generating top DEGs heatmap...\n")

# Combine top DEGs from all comparisons
all_sig_genes <- unique(c(
  comp1$sig_up$gene, comp1$sig_down$gene,
  comp2$sig_up$gene, comp2$sig_down$gene
))

if (length(all_sig_genes) > 100) {
  # Take top 50 by combined significance
  top_heatmap_genes <- bind_rows(
    comp1$res %>% filter(gene %in% all_sig_genes) %>% head(25),
    comp2$res %>% filter(gene %in% all_sig_genes) %>% head(25)
  ) %>% pull(gene) %>% unique()
} else {
  top_heatmap_genes <- all_sig_genes
}

if (length(top_heatmap_genes) > 50) {
  top_heatmap_genes <- head(top_heatmap_genes, 50)
}

mat <- assay(vsd)[top_heatmap_genes, ]
mat_scaled <- t(scale(t(mat)))

# Sort samples by diagnosis
sample_order <- order(colData$diagnosis)
mat_scaled <- mat_scaled[, sample_order]

png("figures/03_deg_heatmap.png", width = 12, height = 10, units = "in", res = 150)
pheatmap(mat_scaled,
         annotation_col = annotation_col,
         annotation_colors = ann_colors,
         show_rownames = TRUE,
         show_colnames = FALSE,
         cluster_cols = FALSE,
         fontsize_row = 6,
         main = "Top Differentially Expressed Genes\nGSE150910",
         color = colorRampPalette(rev(brewer.pal(11, "RdBu")))(255),
         breaks = seq(-2, 2, length.out = 256))
dev.off()
cat("  ✅ Saved: figures/03_deg_heatmap.png\n")

# ═══════════════ 6. GO/KEGG Enrichment ═══════════════
cat("\n🔬 Running GO/KEGG enrichment analysis...\n")

run_enrichment <- function(sig_genes_df, comparison_name, gene_universe) {
  # Convert gene symbols to Entrez IDs
  sig_symbols <- sig_genes_df$gene
  universe_symbols <- gene_universe

  sig_entrez <- bitr(sig_symbols, fromType = "SYMBOL", toType = "ENTREZID",
                     OrgDb = org.Hs.eg.db)
  universe_entrez <- bitr(universe_symbols, fromType = "SYMBOL", toType = "ENTREZID",
                          OrgDb = org.Hs.eg.db)

  if (nrow(sig_entrez) < 5) {
    cat(sprintf("  ⚠️  %s: Too few genes mapped for enrichment\n", comparison_name))
    return(NULL)
  }

  # GO BP
  ego_bp <- enrichGO(
    gene = sig_entrez$ENTREZID,
    universe = universe_entrez$ENTREZID,
    OrgDb = org.Hs.eg.db,
    ont = "BP",
    pAdjustMethod = "BH",
    pvalueCutoff = 0.05,
    qvalueCutoff = 0.1,
    readable = TRUE
  )

  if (!is.null(ego_bp) && nrow(ego_bp) > 0) {
    # Dotplot
    dot_bp <- dotplot(ego_bp, showCategory = 15, title = paste("GO BP:", comparison_name)) +
      theme_minimal(base_size = 11)
    ggsave(sprintf("figures/GO_BP_%s.png", gsub(" ", "_", comparison_name)),
           dot_bp, width = 10, height = 7, dpi = 150)

    # Save table
    write.csv(as.data.frame(ego_bp),
              sprintf("results/GO_BP_%s.csv", gsub(" ", "_", comparison_name)),
              row.names = FALSE)

    cat(sprintf("    GO BP terms: %d\n", nrow(ego_bp)))
  }

  # KEGG (may fail due to network restrictions)
  ekegg <- tryCatch({
    enrichKEGG(
      gene = sig_entrez$ENTREZID,
      universe = universe_entrez$ENTREZID,
      organism = "hsa",
      pAdjustMethod = "BH",
      pvalueCutoff = 0.05,
      qvalueCutoff = 0.1
    )
  }, error = function(e) {
    cat(sprintf("    ⚠️  KEGG enrichment skipped (network error: %s)\n", e$message))
    return(NULL)
  })

  if (!is.null(ekegg) && nrow(ekegg) > 0) {
    dot_kegg <- dotplot(ekegg, showCategory = 15, title = paste("KEGG:", comparison_name)) +
      theme_minimal(base_size = 11)
    ggsave(sprintf("figures/KEGG_%s.png", gsub(" ", "_", comparison_name)),
           dot_kegg, width = 10, height = 7, dpi = 150)

    write.csv(as.data.frame(ekegg),
              sprintf("results/KEGG_%s.csv", gsub(" ", "_", comparison_name)),
              row.names = FALSE)

    cat(sprintf("    KEGG pathways: %d\n", nrow(ekegg)))
  }

  return(list(GO = ego_bp, KEGG = ekegg))
}

universe_genes <- rownames(counts(dds))

# Run enrichment for each comparison's combined up+down DEGs
for (comp in list(comp1, comp2, comp3)) {
  significant <- bind_rows(comp$sig_up, comp$sig_down)
  if (nrow(significant) >= 5) {
    cat(sprintf("\n  📚 Enrichment for %s (%d genes)...\n", comp$contrast, nrow(significant)))
    run_enrichment(significant, comp$contrast, universe_genes)
  }
}

cat("\n\n🎉 All analyses complete!\n")
cat("════════════════════════════════════════\n")
cat("Results saved to:\n")
cat("  results/DEG_*.csv — Full differential expression tables\n")
cat("  results/GO_BP_*.csv — GO enrichment results\n")
cat("  results/KEGG_*.csv — KEGG pathway results\n")
cat("  figures/ — All visualizations\n")
cat("════════════════════════════════════════\n")
