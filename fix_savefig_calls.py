import glob
import re

py_files = [
    "generate_perfect_single_point_figure.py",
    "generate_perfect_stacking_figure.py",
    "generate_perfect_2d_and_3d_cases.py",
    "generate_vibrant_parametric_dashboard.py",
    "generate_four_fields_figure.py",
    "restyle_and_scale_remaining.py",
    "restyler_all_figures.py"
]

for py in py_files:
    with open(py, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix pattern: os.path.join(..., "foo.pdf", format="pdf"
    content = content.replace(', format="pdf"', '')
    content = content.replace(", format='pdf'", '')

    # Ensure all savefig calls save to .pdf
    content = re.sub(r'\.png\b', '.pdf', content)

    with open(py, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Cleaned up savefig calls in: {py}")
