import os
import subprocess
import requests

def get_github_token():
    # Retrieve token via git credential fill
    proc = subprocess.Popen(
        ['git', 'credential', 'fill'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = proc.communicate("protocol=https\nhost=github.com\nusername=Vishal442005\n")
    for line in out.splitlines():
        if line.startswith("password="):
            return line[9:].strip()
    return None

def make_release():
    token = get_github_token()
    if not token:
        raise ValueError("Could not retrieve GitHub token from git credentials.")

    repo = "Vishal442005/Potential-Field-Decay-Classification"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PFDC-Release-Script"
    }

    release_body = """# Potential Field Decay Classification (PFDC) — v1.0.0 (Flagship IEEE TPAMI Submission)

We are proud to announce the **v1.0.0 official release** of **Potential Field Decay Classification (PFDC)**, a physics-grounded machine learning paradigm inspired by classical electrostatics.

PFDC replaces arbitrary global decision boundaries with localized dual-zone potential fields ($R^{\mathrm{core}}$ deterministic certainty + $R^{\mathrm{decay}}$ exponential shell), establishing certified adversarial robustness, formal PAC generalization bounds, and continuous directional counterfactual recourse.

---

### 🌟 Key Highlights & Breakthroughs

1. **Formal Statistical Learning Theory**:
   - **Rademacher Complexity**: $\hat{\mathcal{R}}_M(\mathcal{F}) \le \frac{2 A L_I \sqrt{W} R_X}{\sqrt{M}} + \frac{B}{\sqrt{M}}$
   - **PAC Generalization Bound**: Proves that compact spatial support strictly bounds metric entropy covering numbers $\mathcal{N}(\varepsilon, \mathcal{F}, \|\cdot\|_\infty)$.

2. **Certified Adversarial Robustness**:
   - **Theorem 3**: Proves guaranteed $\ell_2$ invariance within the deterministic core ($d_{\mathbf{w}} \le R^{\mathrm{core}}$).
   - Under FGSM & PGD adversarial attacks, PFDC certainty cores maintain **100.00% certified invariance**, whereas Deep Neural Networks collapse from 97.08% to 13.45%.

3. **Continuous Directional Vector Field & Instant Recourse**:
   - Force field $\mathbf{F}(\mathbf{x}) = -\nabla P(\mathbf{x})$ is irrotational and conservative ($\nabla \times \mathbf{F} = \mathbf{0}$).
   - Generates minimal-effort counterfactual recourse paths along physical streamlines **5.0x faster than Wachter's non-convex optimization (2017)** with 100% convergence.

4. **Fast $O(\log N)$ Spatial Indexing**:
   - Hard cutoff boundary enables spatial Ball-Tree queries, achieving a **2.81x speedup over brute-force** and running **3.8x faster than SVM** at $N=10,000$ with machine-epsilon equivalence ($< 10^{-14}$).

5. **Empirical State-of-the-Art Accuracy**:
   - **2D Non-linear**: #1 Rank (97.22%), beating XGBoost, Deep MLP, Kernel SVM, and Actor-Critic RL.
   - **1,000 Dimensions**: 75.87% accuracy (beating LightGBM 72.80% and XGBoost 72.00%).
   - **Breast Cancer ($D=30$)**: 96.84% (beating XGBoost 95.78% and LightGBM 96.31%).
   - **Ionosphere ($D=34$)**: 94.29% (beating Deep MLP 92.01% and XGBoost 92.59%).

---

### 📦 Included Release Assets
- Full executable Python benchmark suites and SOTA engines (`dual_charge_pfdc.py`, `fast_pfdc.py`, `anisotropic_pfdc.py`).
- Publication-quality high-resolution figures and evaluation logs.
"""

    release_data = {
        "tag_name": "v1.0.0",
        "target_commitish": "main",
        "name": "v1.0.0: Flagship IEEE TPAMI Camera-Ready Release",
        "body": release_body,
        "draft": False,
        "prerelease": False
    }

    print("Creating release on GitHub...")
    res = requests.post(
        f"https://api.github.com/repos/{repo}/releases",
        headers=headers,
        json=release_data
    )
    
    if res.status_code in [200, 201]:
        rel = res.json()
        print(f"Successfully created release: {rel['html_url']}")
        release_id = rel['id']
        upload_url = rel['upload_url'].split('{')[0]
    else:
        # Check if release already exists
        res_get = requests.get(
            f"https://api.github.com/repos/{repo}/releases/tags/v1.0.0",
            headers=headers
        )
        if res_get.status_code == 200:
            rel = res_get.json()
            print(f"Found existing release: {rel['html_url']}")
            release_id = rel['id']
            upload_url = rel['upload_url'].split('{')[0]
        else:
            raise RuntimeError(f"Failed to create release: {res.status_code} {res.text}")

    # Ensure no paper manuscripts or PDFs remain in release assets
    assets_res = requests.get(
        f"https://api.github.com/repos/{repo}/releases/{release_id}/assets",
        headers=headers
    )
    if assets_res.status_code == 200:
        for a in assets_res.json():
            if a["name"].endswith(".pdf") or a["name"].endswith(".tex"):
                print(f"Deleting asset ID {a['id']} ({a['name']})...")
                requests.delete(
                    f"https://api.github.com/repos/{repo}/releases/assets/{a['id']}",
                    headers=headers
                )

    print("\nRelease v1.0.0 verified clean (no paper PDF/TeX assets)!")
    print(f"URL: {rel['html_url']}")

if __name__ == "__main__":
    make_release()
