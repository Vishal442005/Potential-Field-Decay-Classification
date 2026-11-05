import os

with open('tpami_submission/PFDC_TPAMI.tex', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_figure_star = False
in_table_star = False

for line in lines:
    if r'\begin{figure*}' in line:
        in_figure_star = True
    elif in_figure_star and r'\end{figure}' in line and r'\end{figure*}' not in line:
        line = line.replace(r'\end{figure}', r'\end{figure*}')
        in_figure_star = False
    elif in_figure_star and r'\end{figure*}' in line:
        in_figure_star = False

    if r'\begin{table*}' in line:
        in_table_star = True
    elif in_table_star and r'\end{table}' in line and r'\end{table*}' not in line:
        line = line.replace(r'\end{table}', r'\end{table*}')
        in_table_star = False
    elif in_table_star and r'\end{table*}' in line:
        in_table_star = False

    new_lines.append(line)

with open('tpami_submission/PFDC_TPAMI.tex', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed all environment mismatches in tpami_submission/PFDC_TPAMI.tex successfully.")
