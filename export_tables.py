import docx
import os
import csv

doc_path = "Updated_significant/manuscript/PFDC_PatternRecognition.docx"
doc = docx.Document(doc_path)

output_dir = "Updated_significant/tables"
os.makedirs(output_dir, exist_ok=True)

table_names = [
    "Table_01_Architectural_Comparison_PFDC_vs_Baselines",
    "Table_02_Subspace_Stacking_Breast_Cancer",
    "Table_03_Chattering_Optimization_Dynamics",
    "Table_04_Clinical_Hyperparameter_Sweeps",
    "Table_05_2D_Multi_Paradigm_Benchmark",
    "Table_06_1000D_High_Dimensional_Stress_Benchmark",
    "Table_07_Multi_Field_Stratified_5Fold_Cross_Validation",
    "Table_08_Inference_Latency_and_Certified_Invariance",
    "Table_09_Six_Real_World_Datasets_Leaderboard",
    "Table_10_MultiClass_Classification_Benchmark",
    "Table_11_Certified_Adversarial_Robustness_vs_Epsilon",
    "Table_12_Spatial_BallTree_Indexing_Scalability",
    "Table_13_California_Housing_Medium_Scale_Tabular",
    "Table_14_Explainable_AI_Counterfactual_Recourse"
]

print(f"Extracting {len(doc.tables)} tables to {output_dir}...")

for idx, table in enumerate(doc.tables):
    if idx >= len(table_names):
        name = f"Table_{idx+1:02d}"
    else:
        name = table_names[idx]
        
    csv_file = os.path.join(output_dir, f"{name}.csv")
    md_file = os.path.join(output_dir, f"{name}.md")
    
    rows_data = []
    for row in table.rows:
        row_text = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
        rows_data.append(row_text)
        
    # Write CSV
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows_data)
        
    # Write Markdown
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# {name.replace('_', ' ')}\n\n")
        if rows_data:
            headers = rows_data[0]
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
            for r in rows_data[1:]:
                f.write("| " + " | ".join(r) + " |\n")
                
    print(f"Saved: {name} ({len(rows_data)} rows)")

print("All 14 tables exported successfully!")
