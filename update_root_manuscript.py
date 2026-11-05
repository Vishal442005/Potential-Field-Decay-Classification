import os
import shutil

# Read the perfected Elsevier submission tex
with open("elsevier_submission/PFDC_PatternRecognition.tex", "r", encoding="utf-8") as f:
    content = f.read()

# Make it the universal root manuscript
content = content.replace(
    r"\textit{Preprint submitted to Elsevier Pattern Recognition}",
    r"\textit{Research Manuscript --- Gradient Research Laboratory}"
)

with open("PFDC_Manuscript.tex", "w", encoding="utf-8") as f:
    f.write(content)

print(f"PFDC_Manuscript.tex updated successfully. Length: {len(content)} chars")
