# Updated Significant Research Repository: Potential Field Decay Classification (PFDC)

This directory (`Updated_significant/`) aggregates the finalized, publication-grade research manuscript, comprehensive empirical benchmarks, all 14 structured tables, all 23 high-resolution vector figures, deep physical/mathematical trend analyses, and the algorithmic generality synthesis addressing all editorial and peer-review feedback from Elsevier *Pattern Recognition*.

---

## Directory Organization

```
Updated_significant/
├── manuscript/                    # Complete manuscript versions in DOCX, PDF, and LaTeX
│   ├── PFDC_PatternRecognition.docx  # Native Word format with OMML equations, tables & figures
│   ├── PFDC_PR_final.docx            # Camera-ready matching DOCX
│   ├── PFDC_PatternRecognition.pdf   # 70-page camera-ready compiled PDF
│   ├── PFDC_PatternRecognition.tex   # Full unabridged LaTeX source (14 tables, 23 figures)
│   ├── PFDC_TPAMI.docx / .tex        # IEEE TPAMI companion manuscript
│   ├── Cover_Letter.docx             # Submission cover letter
│   ├── Highlights.docx               # Elsevier highlights
│   └── references.bib / .bbl         # Cleaned bibliography without LaTeX tags
│
├── figures/                       # All 23 figures and deep physical trend explanations
│   ├── *.pdf                      # Publication-grade vector PDF figures (Figs. 1 to 23)
│   ├── *.png                      # High-resolution raster renders
│   └── FIGURES_AND_TREND_ANALYSIS.md # Curve-by-curve physical & mathematical explanations
│
├── tables/                        # All 15 empirical tables in individual CSV & Markdown
│   ├── Table_01 to Table_15.csv   # Machine-readable tabular datasets
│   └── Table_01 to Table_15.md    # Formatted Markdown tables with mathematical notes
│
├── results/                       # Raw experimental benchmark results & pivot matrices
│   ├── four_fields_full_benchmark.csv
│   ├── four_fields_accuracy_pivot.csv
│   ├── four_fields_f1_pivot.csv
│   ├── four_fields_latency_pivot.csv
│   ├── pfdc_cases_metrics.csv
│   ├── parametric_sweep_results_table.csv
│   ├── paradigm_benchmark_results.csv
│   ├── anisotropic_comparison_results.csv
│   ├── multidataset_benchmark_results.csv
│   ├── multiclass_benchmark_results.csv
│   ├── adversarial_robustness_results.csv
│   ├── fast_indexing_benchmarks.csv
│   ├── medium_scale_tabnet_benchmarks.csv
│   └── xai_recourse_benchmark.csv
│
└── synthesis_and_generality/      # Archival synthesis of generality & literature baselines
    ├── TAXONOMY_OF_ALGORITHMIC_REGIMES.md  # Operational boundary map & failure modes
    └── EXPANDED_LITERATURE_AND_BASELINE_SYNTHESIS.md # Comparison with 6 similar approaches
```

---

## Key Methodological & Empirical Highlights

1. **Eradication of LaTeX Formatting Artifacts:**
   * All raw LaTeX tags (`\end{thebibliography}`, double dashes `--`, unescaped macros) have been permanently eliminated.
   * All mathematical equations are rendered natively in Microsoft Word using Office Math Markup Language (OMML).
2. **Empirical Authenticity & Parity:**
   * Banknote accuracy: Strictly **$97.23 \pm 1.05\%$** (Macro-F1: $0.9698$).
   * Breast Cancer accuracy: **$96.84 \pm 2.12\%$** (Macro-F1: $0.9663$).
   * Ionosphere Radar accuracy: **$94.29 \pm 2.72\%$** (Macro-F1: $0.9377$).
   * Marine Sonar Dual-Charge accuracy: **$81.28 \pm 4.12\%$** (Macro-F1: $0.8016$).
   * 1,000D Anisotropic accuracy: **$75.87\%$** ($0.5263$ BCE loss, $d_{\mathrm{eff}} \approx 20.0$).
   * Boundary limit-cycle quenching: **$89.7\%$ reduction** ($78 \to 34 \to 8$ sign shifts).
   * Certified Adversarial Invariance: **$100.0\%$ certified immunity** within Certainty Basins ($r_{\mathrm{cert}} = 0.154$).
   * Spatial Ball-Tree Indexing: **$\mathcal{O}(\log N)$ sub-linear query scaling** ($2.81\times$ speedup at $N=10,000$).
   * Explainable AI Recourse: **$5.0\times$ faster convergence** along conservative force streamlines $\mathbf{F} = -\nabla P$.
