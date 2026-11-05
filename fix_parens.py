import re

py_files = [
    'generate_perfect_single_point_figure.py',
    'generate_perfect_stacking_figure.py',
    'generate_perfect_2d_and_3d_cases.py',
    'generate_vibrant_parametric_dashboard.py',
    'generate_four_fields_figure.py',
    'restyle_and_scale_remaining.py'
]

for py in py_files:
    with open(py, 'r', encoding='utf-8') as f:
        c = f.read()

    # Fix pattern 1: os.path.join(OUTPUT_DIR, "something.pdf"
    c = re.sub(r'os\.path\.join\(OUTPUT_DIR,\s*"([^"]+\.pdf)"\s*(?=[,\n])', r'os.path.join(OUTPUT_DIR, "\1")', c)

    # Fix pattern 2: plt.savefig(os.path.join(OUTPUT_DIR, "something.pdf", dpi=300
    c = re.sub(r'plt\.savefig\(os\.path\.join\(OUTPUT_DIR,\s*"([^"]+\.pdf)",\s*', r'plt.savefig(os.path.join(OUTPUT_DIR, "\1"), ', c)

    with open(py, 'w', encoding='utf-8') as f:
        f.write(c)

    print('Fixed parens in:', py)
