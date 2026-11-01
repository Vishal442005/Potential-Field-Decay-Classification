import os
import time
import requests

papers = [
    {
        "id": "1711.00399",
        "filename": "Wachter_2017_Counterfactual_Explanations.pdf",
        "title": "Counterfactual Explanations without Opening the Black Box (Wachter et al., 2017)",
        "url": "https://arxiv.org/pdf/1711.00399.pdf"
    },
    {
        "id": "1706.06083",
        "filename": "Madry_2018_Adversarial_Robustness.pdf",
        "title": "Towards Deep Learning Models Resistant to Adversarial Attacks (Madry et al., 2018)",
        "url": "https://arxiv.org/pdf/1706.06083.pdf"
    },
    {
        "id": "1412.6572",
        "filename": "Goodfellow_2015_Adversarial_Examples.pdf",
        "title": "Explaining and Harnessing Adversarial Examples (Goodfellow et al., 2015)",
        "url": "https://arxiv.org/pdf/1412.6572.pdf"
    },
    {
        "id": "1902.02918",
        "filename": "Cohen_2019_Certified_Adversarial_Robustness.pdf",
        "title": "Certified Adversarial Robustness via Randomized Smoothing (Cohen et al., 2019)",
        "url": "https://arxiv.org/pdf/1902.02918.pdf"
    },
    {
        "id": "1905.07697",
        "filename": "Mothilal_2020_DiCE_Counterfactuals.pdf",
        "title": "Explaining Machine Learning Classifiers through Diverse Counterfactual Explanations (Mothilal et al., 2020)",
        "url": "https://arxiv.org/pdf/1905.07697.pdf"
    },
    {
        "id": "1806.07366",
        "filename": "Chen_2018_Neural_ODEs.pdf",
        "title": "Neural Ordinary Differential Equations (Chen et al., 2018)",
        "url": "https://arxiv.org/pdf/1806.07366.pdf"
    }
]

out_dir = "related_papers"
os.makedirs(out_dir, exist_ok=True)

headers = {
    "User-Agent": "PFDC-Academic-Research/1.0 (mailto:academic-research@gradientlab.org)"
}

print(f"Starting polite download of {len(papers)} related papers into {out_dir}/...\n")

for i, paper in enumerate(papers, 1):
    dest = os.path.join(out_dir, paper["filename"])
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        print(f"[{i}/{len(papers)}] Already downloaded: {paper['filename']} ({os.path.getsize(dest)} bytes)")
        continue

    print(f"[{i}/{len(papers)}] Fetching: {paper['title']}...")
    try:
        resp = requests.get(paper["url"], headers=headers, timeout=30)
        if resp.status_code == 200 and resp.content.startswith(b"%PDF"):
            with open(dest, "wb") as f:
                f.write(resp.content)
            print(f" -> Successfully saved: {dest} ({len(resp.content):,} bytes)")
        else:
            print(f" -> Failed with HTTP {resp.status_code} or invalid PDF header.")
    except Exception as e:
        print(f" -> Error downloading {paper['url']}: {e}")

    # Respect arXiv rate limit policy (1 request every 3 seconds)
    if i < len(papers):
        time.sleep(3.5)

print("\nDownload process completed.")
