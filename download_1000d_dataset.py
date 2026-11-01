import os
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_openml, make_classification
from sklearn.model_selection import train_test_split

def get_high_dimensional_dataset(n_features=1000, n_samples=2500, save_dir="data"):
    """
    Downloads or generates a dataset with at least 1,000 independent variables.
    Splits into train and test sets, and saves them.
    """
    os.makedirs(save_dir, exist_ok=True)
    train_path = os.path.join(save_dir, "dataset_1000d_train.npz")
    test_path = os.path.join(save_dir, "dataset_1000d_test.npz")
    
    if os.path.exists(train_path) and os.path.exists(test_path):
        print(f"Dataset already exists at {save_dir}. Loading...")
        train_data = np.load(train_path)
        test_data = np.load(test_path)
        X_train, y_train = train_data['X'], train_data['y']
        X_test, y_test = test_data['X'], test_data['y']
        print(f"Loaded train shape: {X_train.shape}, test shape: {X_test.shape}")
        return X_train, X_test, y_train, y_test

    print("Attempting to fetch a real high-dimensional dataset (GiSETTE or Madelon-1000D / Leukemia)...")
    download_success = False
    X, y = None, None
    
    # Try fetching Madelon or Gisette from OpenML
    try:
        print("Querying OpenML for GiSETTE (5000 features)...")
        # GiSETTE: OpenML ID 41026 or name 'gisette'
        gisette = fetch_openml('gisette', version=1, as_frame=False, parser='auto')
        X = gisette.data
        # GiSETTE labels are 1 and -1 (or '1' and '-1')
        y = np.where(gisette.target.astype(int) == 1, 1, 0)
        print(f"Successfully downloaded GiSETTE: shape {X.shape}")
        download_success = True
    except Exception as e:
        print(f"OpenML download of GiSETTE failed or timed out ({e}). Trying synthetic 1,000+ independent variables generator...")

    if not download_success:
        print(f"Generating synthetic benchmark dataset with {n_features} independent variables...")
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=int(n_features * 0.1), # 10% informative
            n_redundant=int(n_features * 0.05),  # 5% redundant
            n_clusters_per_class=3,
            weights=[0.5, 0.5],
            flip_y=0.02, # 2% noise
            random_state=42
        )
        print(f"Generated synthetic high-dimensional dataset with shape: {X.shape}, classes: {np.bincount(y)}")

    # Split into 70% train and 30% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )

    print(f"Splitting into Train (70% = {X_train.shape[0]} samples) and Test (30% = {X_test.shape[0]} samples)")
    print(f"Number of independent variables (features): {X_train.shape[1]}")

    # Save to disk
    np.savez_compressed(train_path, X=X_train, y=y_train)
    np.savez_compressed(test_path, X=X_test, y=y_test)
    print(f"Successfully saved to:\n  - {train_path}\n  - {test_path}")

    # Also save a summary info CSV
    summary_df = pd.DataFrame({
        "Metric": ["Total Samples", "Train Samples", "Test Samples", "Independent Variables (Features)", "Classes", "Class Balance (Train 0/1)"],
        "Value": [len(X), len(X_train), len(X_test), X.shape[1], len(np.unique(y)), f"{np.sum(y_train==0)} / {np.sum(y_train==1)}"]
    })
    summary_df.to_csv(os.path.join(save_dir, "dataset_summary.csv"), index=False)
    print("Saved dataset summary to data/dataset_summary.csv")

    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    get_high_dimensional_dataset()
