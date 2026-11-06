# Table 02 Subspace Stacking Breast Cancer

| Subspace Architecture | Learned Variable Weight (w_j) | Test Accuracy (%) | Test F1-Score |
| --- | --- | --- | --- |
| Individual 2D: Radius (x_1) | w_1 = 0.430 | 83.63% | 0.8824 |
| Individual 2D: Texture (x_2) | w_2 = 0.049 | 72.51% | 0.8000 |
| Individual 2D: Perimeter (x_3) | w_3 = 0.334 | 84.80% | 0.8898 |
| Individual 2D: Area (x_4) | w_4 = 0.186 | 83.04% | 0.8807 |
| Composite 2D Overlapped Stacking (All 4 Features) | w^* = [0.430, 0.049, 0.334, 0.186] | 91.81% | 0.9364 |
| Common-Pivot 3D Manifold Stacking (Pivot: Radius x_1) | w_pivot + 3 Subspace Weights | 87.13% | 0.8981 |
